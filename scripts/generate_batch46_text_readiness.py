#!/usr/bin/env python3
"""Classify broad-scan text candidates against the batch46 font expansion."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


BROAD_PATCHABILITY = REPO_ROOT / "rom_analysis" / "broad_scan_patchability.json"
BASE_SLOT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
EXPANSION_PLAN = REPO_ROOT / "rom_analysis" / "next_glyph_expansion_plan.json"
BATCH46_REPORT = REPO_ROOT / "rom_analysis" / "kunio_period_drama_korean_font_expansion_v0.5_batch46_report.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "batch46_text_readiness.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "batch46_text_readiness.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def slot_map(batch_size: int) -> dict[str, dict[str, object]]:
    base = load_json(BASE_SLOT_PLAN)
    expansion = load_json(EXPANSION_PLAN)
    slots = list(base["slots"]) + list(expansion["next_slots"][:batch_size])
    result = {}
    for slot in slots:
        result[str(slot["glyph"])] = {
            "tile": slot["tile"],
            "prg_byte": slot.get("prg_plus_0x7a_byte") or slot.get("planned_prg_byte"),
        }
    return result


def blockers_for(row: dict[str, object], missing: list[str]) -> list[str]:
    blockers = []
    if missing:
        blockers.append("missing glyphs after batch46")
    if int(row.get("bank16", -1)) != 1:
        blockers.append("not Bank 1")
    if bool(row.get("contains_control_like_bytes")):
        blockers.append("source bytes contain control-like values")
    if not bool(row.get("length_equal")):
        blockers.append(
            "length mismatch source_bytes={source_byte_len} korean_glyphs={korean_glyph_len}".format(
                **row
            )
        )
    if int(row.get("priority", 99)) > 15:
        blockers.append("capture priority is not high enough for promotion")
    if str(row.get("confidence")) not in {"high", "medium"}:
        blockers.append("confidence is not high/medium")
    return blockers


def make_payload() -> dict[str, object]:
    broad = load_json(BROAD_PATCHABILITY)
    batch46 = load_json(BATCH46_REPORT)
    slots = slot_map(46)
    v042_ready = [row for row in broad["classified_queue"] if row["font_ready_after_v042"]]

    rows = []
    for row in broad["classified_queue"]:
        glyphs = [str(glyph) for glyph in row["korean_glyphs"]]
        missing = [glyph for glyph in glyphs if glyph not in slots]
        planned = [str(slots[glyph]["prg_byte"]) for glyph in glyphs if glyph in slots]
        blockers = blockers_for(row, missing)
        font_ready = not missing
        newly_font_ready = font_ready and not bool(row["font_ready_after_v042"])
        rows.append(
            {
                "priority": row["priority"],
                "confidence": row["confidence"],
                "rom_offset": row["rom_offset"],
                "bank16": row["bank16"],
                "source": row["source"],
                "romaji": row["romaji"],
                "korean": row["korean"],
                "screen_hint": row["screen_hint"],
                "source_byte_len": row["source_byte_len"],
                "korean_glyph_len": row["korean_glyph_len"],
                "length_equal": row["length_equal"],
                "contains_control_like_bytes": row["contains_control_like_bytes"],
                "font_ready_after_v042": row["font_ready_after_v042"],
                "font_ready_after_batch46": font_ready,
                "newly_font_ready_after_batch46": newly_font_ready,
                "missing_glyphs_after_batch46": missing,
                "planned_prg_bytes_after_batch46": planned,
                "promotable_after_batch46_screen_proof": not blockers,
                "blockers_after_batch46": blockers,
            }
        )

    font_ready = [row for row in rows if row["font_ready_after_batch46"]]
    newly_ready = [row for row in rows if row["newly_font_ready_after_batch46"]]
    promotable = [row for row in rows if row["promotable_after_batch46_screen_proof"]]
    newly_promotable = [row for row in promotable if row["newly_font_ready_after_batch46"]]

    return {
        "source": {
            "broad_patchability": rel(BROAD_PATCHABILITY),
            "base_slot_plan": rel(BASE_SLOT_PLAN),
            "expansion_plan": rel(EXPANSION_PLAN),
            "batch46_report": rel(BATCH46_REPORT),
        },
        "summary": {
            "queued_hits": len(rows),
            "batch46_added_glyphs": batch46["added_glyph_count"],
            "v042_font_ready": len(v042_ready),
            "batch46_font_ready": len(font_ready),
            "newly_font_ready_after_batch46": len(newly_ready),
            "screen_proof_candidates_after_batch46": len(promotable),
            "new_screen_proof_candidates_after_batch46": len(newly_promotable),
            "rule": "Batch46 expands font coverage only; text promotion still requires manual CPU-read and visual-context proof.",
        },
        "newly_font_ready": newly_ready,
        "screen_proof_candidates": promotable,
        "classified_queue": rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Batch46 Text Readiness",
        "",
        "This report reclassifies the broad-scan capture queue against the largest currently buildable font expansion.",
        "",
        "## Summary",
        "",
        f"- Queued hits: **{summary['queued_hits']}**",
        f"- Batch46 added glyphs: **{summary['batch46_added_glyphs']}**",
        f"- Font-ready after v0.4.2: **{summary['v042_font_ready']}**",
        f"- Font-ready after batch46: **{summary['batch46_font_ready']}**",
        f"- Newly font-ready after batch46: **{summary['newly_font_ready_after_batch46']}**",
        f"- Screen-proof candidates after batch46: **{summary['screen_proof_candidates_after_batch46']}**",
        f"- New screen-proof candidates after batch46: **{summary['new_screen_proof_candidates_after_batch46']}**",
        "",
        "## New Font-Ready Rows",
        "",
        "| priority | confidence | ROM | romaji | bytes | glyphs | blockers |",
        "| ---: | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in payload["newly_font_ready"]:
        lines.append(
            f"| {row['priority']} | {row['confidence']} | `{row['rom_offset']}` | "
            f"{row['romaji']} | {row['source_byte_len']} | {row['korean_glyph_len']} | "
            f"{'; '.join(row['blockers_after_batch46']) or 'manual screen proof'} |"
        )

    lines += [
        "",
        "## Screen-Proof Candidates",
        "",
        "| priority | confidence | ROM | romaji | korean | planned bytes | screen hint |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["screen_proof_candidates"]:
        lines.append(
            f"| {row['priority']} | {row['confidence']} | `{row['rom_offset']}` | "
            f"{row['romaji']} | {row['korean']} | "
            f"`{' '.join(row['planned_prg_bytes_after_batch46'])}` | {row['screen_hint']} |"
        )

    lines += [
        "",
        "## Rule",
        "",
        "- Do not promote rows from font readiness alone.",
        "- A row can move into a patch only after manual CPU-read evidence and visible screen-context proof agree.",
        "- Rows blocked by length mismatch still need a padding/control-code rule before patching.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "batch46_font_ready={batch46_font_ready} new_font_ready={newly_font_ready_after_batch46} screen_candidates={screen_proof_candidates_after_batch46}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

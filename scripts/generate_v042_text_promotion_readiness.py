#!/usr/bin/env python3
"""Report which broad-scan text candidates are font-ready under v0.4.2."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


BROAD_PATCHABILITY = REPO_ROOT / "rom_analysis" / "broad_scan_patchability.json"
BASE_SLOT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
EXPANSION_PLAN = REPO_ROOT / "rom_analysis" / "next_glyph_expansion_plan.json"
V042_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded_build_report.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "v042_text_promotion_readiness.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "v042_text_promotion_readiness.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def slot_map_for_v042() -> dict[str, dict[str, object]]:
    base = load_json(BASE_SLOT_PLAN)
    expansion = load_json(EXPANSION_PLAN)
    slots = list(base["slots"]) + list(expansion["next_slots"][:32])
    by_glyph = {}
    for slot in slots:
        byte = slot.get("prg_plus_0x7a_byte") or slot.get("planned_prg_byte")
        by_glyph[str(slot["glyph"])] = {
            "tile": slot["tile"],
            "prg_byte": byte,
        }
    return by_glyph


def row_kind(row: dict[str, object]) -> str:
    confidence = str(row.get("confidence", ""))
    if confidence == "high":
        return "conflict_alternative_needs_manual_screen"
    return "non_overlapping_needs_manual_screen"


def make_payload() -> dict[str, object]:
    broad = load_json(BROAD_PATCHABILITY)
    v042 = load_json(V042_REPORT)
    slots = slot_map_for_v042()
    applied_offsets = {str(row["rom_hit"]).upper() for row in v042.get("applied", [])}
    skipped_offsets = {str(row["rom_hit"]).upper() for row in v042.get("skipped", [])}

    candidates = []
    for row in broad["promotion_candidates"]:
        glyphs = list(row["korean_glyphs"])
        missing = [glyph for glyph in glyphs if glyph not in slots]
        planned = [slots[glyph]["prg_byte"] for glyph in glyphs if glyph in slots]
        rom_offset = str(row["rom_offset"]).upper()
        candidates.append(
            {
                "kind": row_kind(row),
                "confidence": row.get("confidence", ""),
                "source": row.get("source", ""),
                "korean": row.get("korean", ""),
                "rom_offset": row.get("rom_offset", ""),
                "bank16": row.get("bank16", ""),
                "original_bytes": row.get("bytes", ""),
                "korean_glyphs": glyphs,
                "planned_prg_bytes": planned,
                "font_ready_v042": not missing,
                "missing_glyphs_after_v042": missing,
                "already_applied_in_v042": rom_offset in applied_offsets,
                "skipped_in_v042": rom_offset in skipped_offsets,
                "next_gate": "manual screen proof with base ROM broad-scan dump",
                "capture_lua": "lua/kunio_manual_broad_scan_dump.lua",
                "summary_command": "python scripts/analyze_broad_scan_manual_dump.py",
            }
        )

    font_ready = [row for row in candidates if row["font_ready_v042"]]
    non_overlap = [row for row in font_ready if row["kind"] == "non_overlapping_needs_manual_screen"]
    conflicts = [row for row in font_ready if row["kind"] == "conflict_alternative_needs_manual_screen"]
    return {
        "source": {
            "broad_patchability": rel(BROAD_PATCHABILITY),
            "base_slot_plan": rel(BASE_SLOT_PLAN),
            "expansion_plan": rel(EXPANSION_PLAN),
            "v042_report": rel(V042_REPORT),
        },
        "summary": {
            "promotion_candidates": len(candidates),
            "font_ready_after_v042": len(font_ready),
            "missing_glyph_after_v042": len(candidates) - len(font_ready),
            "non_overlapping_font_ready": len(non_overlap),
            "conflict_alternatives_font_ready": len(conflicts),
            "rule": "v0.4.2 font coverage removes the glyph blocker, but every candidate still needs manual screen proof before patching.",
        },
        "candidates": candidates,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# v0.4.2 Text Promotion Readiness",
        "",
        "This report shows which broad-scan text candidates are now font-ready under the v0.4.2 expanded glyph set.",
        "",
        "## Summary",
        "",
        f"- Broad promotion candidates: **{summary['promotion_candidates']}**",
        f"- Font-ready after v0.4.2: **{summary['font_ready_after_v042']}**",
        f"- Still missing glyphs: **{summary['missing_glyph_after_v042']}**",
        f"- Non-overlapping font-ready candidates: **{summary['non_overlapping_font_ready']}**",
        f"- Conflict-alternative font-ready candidates: **{summary['conflict_alternatives_font_ready']}**",
        "",
        "## Candidates",
        "",
        "| kind | confidence | ROM | source | korean | original bytes | planned bytes | gate |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["candidates"]:
        lines.append(
            f"| `{row['kind']}` | {row['confidence']} | `{row['rom_offset']}` | "
            f"{row['source']} | {row['korean']} | `{row['original_bytes']}` | "
            f"`{' '.join(row['planned_prg_bytes'])}` | {row['next_gate']} |"
        )

    lines += [
        "",
        "## How To Prove One",
        "",
        "1. Open the base Japanese ROM in FCEUX.",
        "2. Manually reach the screen where the candidate text appears.",
        "3. Run `lua/kunio_manual_broad_scan_dump.lua`.",
        "4. Run `python scripts/analyze_broad_scan_manual_dump.py`.",
        "5. Promote only if the byte match and visible screen context agree.",
        "",
        "## Rule",
        "",
        "- Do not promote these rows from static evidence alone.",
        "- v0.4.2 means glyphs are ready; it does not prove the ROM offset is the visible text instance.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "candidates={promotion_candidates} font_ready={font_ready_after_v042} non_overlap={non_overlapping_font_ready}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

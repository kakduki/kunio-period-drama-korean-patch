#!/usr/bin/env python3
"""Create a transcript/reference-guided capture plan for broad-scan candidates."""

from __future__ import annotations

import json
import re
from pathlib import Path

from rom_utils import REPO_ROOT


QUEUE_JSON = REPO_ROOT / "rom_analysis" / "translation_scan_capture_queue.json"
PATCHABILITY_JSON = REPO_ROOT / "rom_analysis" / "broad_scan_patchability.json"
PROOF_STATUS_JSON = REPO_ROOT / "rom_analysis" / "v043_proof_status.json"
REFERENCE_JSON = REPO_ROOT / "text_data" / "translation_readable_reference.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "reference_capture_plan.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "reference_capture_plan.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def section_number(section: object) -> int:
    match = re.match(r"\s*(\d+)", str(section or ""))
    return int(match.group(1)) if match else 99


def patchability_by_offset() -> dict[str, dict[str, object]]:
    payload = load_json(PATCHABILITY_JSON)
    return {
        str(row["rom_offset"]).upper(): row
        for row in payload.get("classified_queue", [])
    }


def proof_by_offset() -> dict[str, dict[str, object]]:
    payload = load_json(PROOF_STATUS_JSON)
    return {
        str(row["rom_offset"]).upper(): row
        for row in payload.get("rows", [])
    }


def source_order() -> dict[str, int]:
    reference = load_json(REFERENCE_JSON)
    order: dict[str, int] = {}
    for index, row in enumerate(reference.get("translation_data_joined", []), start=1):
        source = str(row.get("source", ""))
        order.setdefault(source, index)
    return order


def capture_score(row: dict[str, object], patch_row: dict[str, object], proof_row: dict[str, object]) -> int:
    score = 1000
    score -= section_number(row.get("reference_section")) * 40
    if patch_row.get("promotable_after_screen_proof"):
        score += 300
    if patch_row.get("font_ready_after_v042"):
        score += 120
    confidence = str(row.get("confidence", ""))
    if confidence == "high":
        score += 120
    elif confidence == "medium":
        score += 60
    if proof_row.get("status") == "needs_manual_capture":
        score += 40
    if int(row.get("bank16", 99)) == 1:
        score += 40
    return score


def make_payload() -> dict[str, object]:
    queue = load_json(QUEUE_JSON)
    patches = patchability_by_offset()
    proof = proof_by_offset()
    order = source_order()
    rows = []
    for row in queue.get("queue", []):
        offset = str(row["rom_offset"]).upper()
        patch_row = patches.get(offset, {})
        proof_row = proof.get(offset, {})
        section = str(row.get("reference_section", ""))
        capture_row = {
            "rank_score": capture_score(row, patch_row, proof_row),
            "reference_order": order.get(str(row.get("source_display") or row.get("source")), 9999),
            "reference_section": section,
            "section_number": section_number(section),
            "confidence": row.get("confidence", ""),
            "rom_offset": row.get("rom_offset", ""),
            "bank16": row.get("bank16", ""),
            "cpu_address_guess": row.get("cpu_address_guess", ""),
            "source_display": row.get("source_display") or row.get("source", ""),
            "korean_display": row.get("korean_display") or row.get("korean", ""),
            "romaji": row.get("romaji", ""),
            "screen_hint": row.get("screen_hint", ""),
            "promotable_after_screen_proof": bool(patch_row.get("promotable_after_screen_proof")),
            "font_ready_after_v042": bool(patch_row.get("font_ready_after_v042")),
            "planned_prg_bytes_after_v042": patch_row.get("planned_prg_bytes_after_v042", []),
            "proof_status": proof_row.get("status", "not_in_v043_proof_packet"),
            "why": "reference order narrows screen search; ROM promotion still requires CPU-read and visual proof",
        }
        rows.append(capture_row)

    rows.sort(
        key=lambda row: (
            -int(row["rank_score"]),
            int(row["reference_order"]),
            int(row["section_number"]),
            str(row["rom_offset"]),
        )
    )
    focused = rows[:20]
    return {
        "source": {
            "queue": str(QUEUE_JSON.relative_to(REPO_ROOT)),
            "patchability": str(PATCHABILITY_JSON.relative_to(REPO_ROOT)),
            "proof_status": str(PROOF_STATUS_JSON.relative_to(REPO_ROOT)),
            "reference": str(REFERENCE_JSON.relative_to(REPO_ROOT)),
        },
        "summary": {
            "queue_rows": len(rows),
            "focused_rows": len(focused),
            "promotable_focused_rows": sum(1 for row in focused if row["promotable_after_screen_proof"]),
            "font_ready_focused_rows": sum(1 for row in focused if row["font_ready_after_v042"]),
            "rule": "Use the transcript/reference only to choose screens to reach; never as proof for patch promotion.",
        },
        "focused_capture_plan": focused,
        "all_ranked_rows": rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Reference-Guided Capture Plan",
        "",
        "This plan uses the text transcription/reference to choose which screens are worth reaching manually.",
        "It does not treat YouTube or transcription order as ROM proof.",
        "",
        "## Summary",
        "",
        f"- Queue rows: **{summary['queue_rows']}**",
        f"- Focused rows: **{summary['focused_rows']}**",
        f"- Focused rows that are length-safe promotion candidates: **{summary['promotable_focused_rows']}**",
        f"- Focused rows font-ready after v0.4.2: **{summary['font_ready_focused_rows']}**",
        "",
        "## Focused Capture Plan",
        "",
        "| rank | score | section | ROM | expected text | Korean | CPU guess | proof status | v0.4.2 bytes | screen hint |",
        "| ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(payload["focused_capture_plan"], start=1):
        planned = " ".join(row.get("planned_prg_bytes_after_v042", [])) or "-"
        lines.append(
            f"| {index} | {row['rank_score']} | {row['reference_section'] or '-'} | `{row['rom_offset']}` | "
            f"{row['source_display']} | {row['korean_display']} | `{row['cpu_address_guess']}` | "
            f"`{row['proof_status']}` | `{planned}` | {row['screen_hint']} |"
        )

    lines += [
        "",
        "## Rule",
        "",
        "- This file is a navigation aid for FCEUX/manual video review.",
        "- A row becomes patchable only after `v043_proof_status.md` shows CPU-read proof and visual confirmation.",
        "- Stop any autoplay route that stays on the title/first screen; use this plan to pick a concrete screen instead.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "focused={focused_rows} promotable={promotable_focused_rows} font_ready={font_ready_focused_rows}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

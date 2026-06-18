#!/usr/bin/env python3
"""Triage whether the current auto-input capture can satisfy visual-review targets."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


EVIDENCE_JSON = REPO_ROOT / "rom_analysis" / "auto_input_evidence_report.json"
NEXT_MANUAL_RUN_JSON = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
REVIEW_CROPS_JSON = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "review_crops.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "auto_input_visual_triage.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "auto_input_visual_triage.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_dialogue_crop(crops: dict[str, object]) -> str:
    dialogue = [
        row for row in crops.get("crops", [])
        if isinstance(row, dict) and row.get("crop") == "dialogue_box"
    ]
    if not dialogue:
        return ""
    dialogue.sort(key=lambda row: str(row.get("path", "")))
    return str(dialogue[-1].get("path", ""))


def make_payload() -> dict[str, object]:
    evidence = load_json(EVIDENCE_JSON)
    next_run = load_json(NEXT_MANUAL_RUN_JSON)
    crops = load_json(REVIEW_CROPS_JSON)
    next_action = next_run.get("next_action") if isinstance(next_run.get("next_action"), dict) else {}
    evidence_summary = evidence["summary"]

    visual_approval_rows = []
    for row in evidence.get("matched_rows", []):
        if not isinstance(row, dict):
            continue
        visual_approval_rows.append(
            {
                "rom_hit": row.get("rom_hit", ""),
                "romaji": row.get("romaji", ""),
                "byte_match": True,
                "visual_context_confirmed": False,
                "reason": "current auto-input capture is opening dialogue evidence, not the target visual context",
            }
        )

    return {
        "source": {
            "auto_input_evidence_report": str(EVIDENCE_JSON.relative_to(REPO_ROOT)),
            "next_manual_run": str(NEXT_MANUAL_RUN_JSON.relative_to(REPO_ROOT)),
            "review_crops": str(REVIEW_CROPS_JSON.relative_to(REPO_ROOT)),
        },
        "summary": {
            "current_auto_route_scene": "opening_dialogue",
            "latest_dialogue_crop": latest_dialogue_crop(crops),
            "byte_matched_primary_rows": evidence_summary.get("matched_primary_rows", 0),
            "visual_approval_rows": 0,
            "next_visual_target": next_action.get("target", ""),
            "next_visual_group": next_action.get("group", ""),
            "next_visual_hint": next_action.get("screen_hint", ""),
            "decision": (
                "Do not mark any primary row visually confirmed from this auto-input capture. "
                "Use it as route/byte-load evidence and adjust the next route toward the target context."
            ),
        },
        "rows": visual_approval_rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Auto-Input Visual Triage",
        "",
        "This separates byte-load evidence from final visual approval for the current scripted route.",
        "",
        "## Decision",
        "",
        f"- Current auto-route scene: `{summary['current_auto_route_scene']}`",
        f"- Latest dialogue crop: `{summary['latest_dialogue_crop']}`",
        f"- Byte-matched primary rows: **{summary['byte_matched_primary_rows']}**",
        f"- Visual approvals from this capture: **{summary['visual_approval_rows']}**",
        f"- Next visual target: `{summary['next_visual_target']}` / {summary['next_visual_group']}",
        f"- Next visual hint: {summary['next_visual_hint']}",
        f"- Decision: {summary['decision']}",
        "",
        "## Row Triage",
        "",
        "| ROM | romaji | byte match | visual confirmed | reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['rom_hit']}` | {row['romaji'] or '-'} | {str(row['byte_match']).lower()} | "
            f"{str(row['visual_context_confirmed']).lower()} | {row['reason']} |"
        )
    lines += [
        "",
        "## Next Step",
        "",
        "- Keep the auto-input route evidence, but route the emulator to the `Katana` item/weapon label before recording visual approval.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"visual_approval_rows={payload['summary']['visual_approval_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

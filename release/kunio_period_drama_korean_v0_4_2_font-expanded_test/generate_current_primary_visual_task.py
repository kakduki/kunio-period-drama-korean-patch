#!/usr/bin/env python3
"""Generate the single current primary visual-proof task."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


NEXT_MANUAL_RUN = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
PRIMARY_VISUAL_CHECKLIST = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
AUTO_INPUT_SUMMARY = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "summary.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "current_primary_visual_task.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "current_primary_visual_task.md"

CONTEXT_REJECTION_BY_TARGET = {
    "0x0569D": {
        "status": "CONTEXT_REJECTED_DIALOGUE_NOT_LOCATION_LABEL",
        "reason": (
            "The existing auto-input PNG reaches an in-game dialogue/background scene; "
            "it is not a clear bridge/stage/location label screen."
        ),
        "required_screen": "A patched-ROM screen where the Hashi bridge/stage/location label is visibly displayed.",
    }
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path_text: str) -> str:
    return path_text.replace("\\", "/")


def find_primary_row(target: str, checklist: dict[str, object]) -> dict[str, object]:
    for row in checklist.get("rows", []):
        row_target = str(row.get("rom_hit") or row.get("rom_offset") or "").lower()
        if row_target == target.lower():
            return row
    return {}


def find_auto_match(target: str, summary: dict[str, object]) -> dict[str, object]:
    needle = "ROM+" + target.lower().replace("0x", "0x").upper()
    for row in summary.get("active_matches", []):
        if str(row.get("rom_hit", "")).upper() == needle:
            return row
    return {}


def build_payload() -> dict[str, object]:
    next_run = load_json(NEXT_MANUAL_RUN)
    checklist = load_json(PRIMARY_VISUAL_CHECKLIST)
    auto_summary = load_json(AUTO_INPUT_SUMMARY)
    next_action = next_run.get("next_action", {})
    if not isinstance(next_action, dict):
        raise ValueError("next_manual_run.json has no next_action object")
    if next_action.get("phase") != "primary_v042_visual_review":
        raise ValueError(f"next action is not primary visual review: {next_action.get('phase')}")

    target = str(next_action.get("target", ""))
    primary_row = find_primary_row(target, checklist)
    auto_match = find_auto_match(target, auto_summary)
    context = CONTEXT_REJECTION_BY_TARGET.get(
        target,
        {
            "status": "NEEDS_MANUAL_CONTEXT_REVIEW",
            "reason": "No target-specific context decision has been recorded for the existing auto-input PNG.",
            "required_screen": str(next_action.get("screen_hint", "visible matching target screen")),
        },
    )

    auto_context_status = context["status"] if auto_match else "NO_AUTO_INPUT_MATCH"
    decision = "NEEDS_MANUAL_VISUAL_PROOF"
    return {
        "source": {
            "next_manual_run": rel(str(NEXT_MANUAL_RUN.relative_to(REPO_ROOT))),
            "primary_visual_checklist": rel(str(PRIMARY_VISUAL_CHECKLIST.relative_to(REPO_ROOT))),
            "auto_input_summary": rel(str(AUTO_INPUT_SUMMARY.relative_to(REPO_ROOT))),
        },
        "summary": {
            "target": target,
            "group": next_action.get("group", ""),
            "phase": next_action.get("phase", ""),
            "decision": decision,
            "auto_input_byte_match": bool(auto_match),
            "auto_input_context_status": auto_context_status,
            "can_confirm_from_existing_auto_input": False,
            "required_screen": context["required_screen"],
            "rule": "Byte matches can guide capture work, but they do not approve visual review without the expected visible screen context.",
        },
        "next_action": next_action,
        "primary_visual_row": primary_row,
        "existing_auto_input_evidence": {
            "frame": auto_match.get("frame", auto_summary.get("frame", "")),
            "png": rel(str(auto_summary.get("latest_png_review_image", ""))),
            "target_records": rel(str(auto_summary.get("input_records", ""))),
            "record_snapshot": auto_match.get("record_snapshot", ""),
            "expected_bytes": auto_match.get("expected_bytes", ""),
            "visual_route_note": auto_summary.get("visual_route_note", ""),
            "context_rejection_reason": context["reason"],
        },
        "commands": {
            "preflight": "python scripts/preflight_manual_fceux.py",
            "launch": "python scripts/run_next_manual_fceux.py",
            "confirm_after_visible_match": "python scripts/confirm_next_primary_visual.py --confirm-visible",
            "refresh_after_direct_fceux": "python scripts/refresh_after_manual_capture.py --phase primary",
        },
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    action = payload["next_action"]
    evidence = payload["existing_auto_input_evidence"]
    commands = payload["commands"]
    lines = [
        "# Current Primary Visual Task",
        "",
        f"- Decision: `{summary['decision']}`",
        f"- Target: `{summary['target']}` / {summary['group']}",
        f"- ROM to open: `{action.get('rom_to_open', '')}`",
        f"- Watcher Lua: `{action.get('watcher_lua', '')}`",
        f"- Required screen: {summary['required_screen']}",
        f"- Existing auto-input byte match: `{summary['auto_input_byte_match']}`",
        f"- Existing auto-input context status: `{summary['auto_input_context_status']}`",
        f"- Existing PNG: `{evidence['png']}`",
        f"- Existing target records: `{evidence['target_records']}`",
        f"- Existing record snapshot: `{evidence['record_snapshot']}`",
        f"- Why not auto-approved: {evidence['context_rejection_reason']}",
        "",
        "## Commands",
        "",
        "```powershell",
        commands["preflight"],
        commands["launch"],
        commands["confirm_after_visible_match"],
        "```",
        "",
        "Only run the confirm command after the patched-ROM screen visibly matches the required screen.",
        "If FCEUX remains on the title/opening screen, stop the run instead of waiting longer.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"decision={payload['summary']['decision']}")
    print(f"target={payload['summary']['target']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

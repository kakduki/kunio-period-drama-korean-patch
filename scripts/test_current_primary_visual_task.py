#!/usr/bin/env python3
"""Check the generated current primary visual task."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


TASK_JSON = REPO_ROOT / "rom_analysis" / "current_primary_visual_task.json"
TASK_MD = REPO_ROOT / "rom_analysis" / "current_primary_visual_task.md"


def main() -> int:
    payload = json.loads(TASK_JSON.read_text(encoding="utf-8"))
    summary = payload["summary"]
    evidence = payload["existing_auto_input_evidence"]
    errors: list[str] = []

    expected = {
        "target": "0x0569D",
        "group": "Hashi",
        "decision": "NEEDS_MANUAL_VISUAL_PROOF",
        "auto_input_byte_match": True,
        "auto_input_context_status": "CONTEXT_REJECTED_DIALOGUE_NOT_LOCATION_LABEL",
        "can_confirm_from_existing_auto_input": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"{key}: expected {value!r}, got {summary.get(key)!r}")
    if "85 8B 8C FF" not in str(evidence.get("record_snapshot", "")):
        errors.append("Hashi auto-input record snapshot is missing")
    if "not a clear bridge/stage/location label" not in str(evidence.get("context_rejection_reason", "")):
        errors.append("context rejection reason does not explain the screen mismatch")

    markdown = TASK_MD.read_text(encoding="utf-8")
    for text in [
        "Current Primary Visual Task",
        "0x0569D",
        "Hashi",
        "NEEDS_MANUAL_VISUAL_PROOF",
        "CONTEXT_REJECTED_DIALOGUE_NOT_LOCATION_LABEL",
        "python scripts/run_next_manual_fceux.py",
        "If FCEUX remains on the title/opening screen, stop the run instead of waiting longer.",
    ]:
        if text not in markdown:
            errors.append(f"{text!r} missing from markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: current primary visual task rejects the existing wrong-context auto-input frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

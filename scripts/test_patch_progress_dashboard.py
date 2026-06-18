#!/usr/bin/env python3
"""Check the generated patch progress dashboard."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


DASHBOARD_JSON = REPO_ROOT / "rom_analysis" / "patch_progress_dashboard.json"
DASHBOARD_MD = REPO_ROOT / "rom_analysis" / "patch_progress_dashboard.md"


def main() -> int:
    payload = json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
    summary = payload["summary"]
    errors: list[str] = []

    expected = {
        "primary_candidate": "v0.4.2 font-expanded",
        "primary_applied_rows": 10,
        "pending_manual_actions": 13,
        "pending_primary_visual_checks": 10,
        "pending_v043_route_proofs": 3,
        "primary_auto_input_match_rows": 10,
        "v043_rows": 7,
        "manual_dump_record_files": 0,
        "release_ready": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"{key}: expected {value!r}, got {summary.get(key)!r}")
    if not summary.get("release_blockers"):
        errors.append("release blockers are missing")

    next_action = payload.get("next_action")
    if not isinstance(next_action, dict) or next_action.get("target") != "0x07227":
        errors.append(f"unexpected next action: {next_action!r}")

    markdown = DASHBOARD_MD.read_text(encoding="utf-8")
    for expected_text in [
        "Patch Progress Dashboard",
        "Release Blockers",
        "python scripts/preflight_manual_fceux.py",
        "python scripts/run_next_manual_fceux.py",
        "python scripts/confirm_next_primary_visual.py --confirm-visible",
        "python scripts/prepare_next_manual_run.py --powershell",
        "0x07227",
        "Auto-input byte-match rows",
    ]:
        if expected_text not in markdown:
            errors.append(f"{expected_text!r} missing from dashboard markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: patch progress dashboard summarizes the current release blockers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Confirm the current next primary visual-review row, then refresh reports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from preflight_manual_fceux import load_next_manual_context
from rom_utils import REPO_ROOT


PRIMARY_VISUAL_CHECKLIST = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"


def manual_record_count(target: object) -> int:
    if not PRIMARY_VISUAL_CHECKLIST.exists():
        return 0
    payload = json.loads(PRIMARY_VISUAL_CHECKLIST.read_text(encoding="utf-8"))
    for row in payload.get("rows", []):
        if isinstance(row, dict) and row.get("rom_hit") == target:
            return int(row.get("record_file_count", 0) or 0)
    return 0


def build_commands(action: dict[str, object], screen_context: str) -> list[list[str]]:
    return [
        ["scripts/refresh_after_manual_capture.py", "--phase", "primary"],
        [
            "scripts/record_primary_visual_review.py",
            str(action["target"]),
            "--confirm",
            "--screen-context",
            screen_context,
        ],
        ["scripts/refresh_after_manual_capture.py", "--phase", "primary"],
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-visible",
        action="store_true",
        help="Required. Use only after the visible patched-ROM screen matches the target.",
    )
    parser.add_argument("--screen-context", default="", help="Short note about the visible matching screen.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without changing review files.")
    args = parser.parse_args()

    context = load_next_manual_context()
    action = context.get("action")
    if not isinstance(action, dict):
        print("No pending manual action.")
        return 0
    if action.get("phase") != "primary_v042_visual_review":
        print(f"ERROR: next action is not a primary visual review: {action.get('phase')}")
        return 1
    if not args.confirm_visible:
        print("ERROR: pass --confirm-visible after checking the matching screen in FCEUX.")
        return 1

    screen_context = args.screen_context or f"{action['screen_hint']} visible"
    commands = build_commands(action, screen_context)
    print(f"Confirming primary visual review: {action['target']} / {action['group']}")
    print("Command order: refresh manual dumps, record the visible-screen review, then refresh the queue.")
    for command in commands:
        print(" ".join([sys.executable, *command]))

    if args.dry_run:
        record_count = manual_record_count(action["target"])
        if record_count == 0:
            print("WARNING: no manual dump record is currently indexed for this target. Press D in FCEUX before confirming when possible.")
        else:
            print(f"Manual dump records indexed for this target: {record_count}")
        return 0

    subprocess.run([sys.executable, *commands[0]], cwd=REPO_ROOT, check=True)
    record_count = manual_record_count(action["target"])
    if record_count == 0:
        print("WARNING: no manual dump record is currently indexed for this target. Press D in FCEUX before confirming when possible.")
    else:
        print(f"Manual dump records indexed for this target: {record_count}")
    for command in commands[1:]:
        subprocess.run([sys.executable, *command], cwd=REPO_ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

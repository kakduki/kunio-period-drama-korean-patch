#!/usr/bin/env python3
"""Run the current next manual FCEUX capture action."""

from __future__ import annotations

import argparse
import subprocess
import sys

from preflight_manual_fceux import (
    DEFAULT_MANUAL_TIMEOUT,
    launch_command,
    load_next_manual_context,
    validate_next_action,
)
from rom_utils import REPO_ROOT


def manual_dump_records() -> set[str]:
    return {
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in (REPO_ROOT / "rom_analysis").glob("manual_screen_dump*/manual_frame_*_target_records.tsv")
    }


def after_capture_commands(action: dict[str, object]) -> list[list[str]]:
    commands = []
    for raw in action.get("after_capture", []):
        if raw == "python scripts/refresh_after_manual_capture.py --phase primary":
            commands.append(["scripts/refresh_after_manual_capture.py", "--phase", "primary"])
        elif raw == "python scripts/refresh_after_manual_capture.py --phase broad":
            commands.append(["scripts/refresh_after_manual_capture.py", "--phase", "broad"])
        else:
            print(f"WARNING: unsupported after_capture command skipped: {raw}")
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=DEFAULT_MANUAL_TIMEOUT)
    parser.add_argument("--dry-run", action="store_true", help="Print the launch command without opening FCEUX.")
    args = parser.parse_args()

    context = load_next_manual_context()
    action = context.get("action")
    if not isinstance(action, dict):
        print("No pending manual FCEUX action.")
        return 0

    errors, warnings = validate_next_action(context)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    command = launch_command(action, timeout=args.timeout)
    task = context.get("current_visual_task", {})
    task_summary = task.get("summary", {}) if isinstance(task, dict) else {}
    task_evidence = task.get("existing_auto_input_evidence", {}) if isinstance(task, dict) else {}
    print(f"Next manual FCEUX action: {action['target']} / {action['group']}")
    print(f"Hint: {action['screen_hint']}")
    if task_summary:
        print(f"Required screen: {task_summary.get('required_screen', '')}")
        print(f"Existing auto-input context: {task_summary.get('auto_input_context_status', '')}")
        if task_evidence.get("context_rejection_reason"):
            print(f"Why existing PNG is not enough: {task_evidence['context_rejection_reason']}")
    print("This launcher does not autoplay through the game.")
    print("Use FCEUX controls to reach the target screen, then press D in FCEUX. The launcher stops after the dump.")
    print("Launch command:")
    print(" ".join([sys.executable, *command]))

    if args.dry_run:
        return 0

    before = manual_dump_records()
    result = subprocess.run([sys.executable, *command], cwd=REPO_ROOT)
    after = manual_dump_records()
    new_records = sorted(after - before)
    if new_records:
        print("New manual dump record(s):")
        for record in new_records:
            print(f"- {record}")
        for after_command in after_capture_commands(action):
            print("Running after-capture refresh:")
            print(" ".join([sys.executable, *after_command]))
            subprocess.run([sys.executable, *after_command], cwd=REPO_ROOT, check=True)
    else:
        print(
            "No new manual dump record was created. If FCEUX stayed on the title/opening screen, "
            "this run did not add patch evidence; manually enter the target screen and press D."
        )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

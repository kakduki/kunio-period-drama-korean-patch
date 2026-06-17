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
    print(f"Next manual FCEUX action: {action['target']} / {action['group']}")
    print(f"Hint: {action['screen_hint']}")
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
    else:
        print(
            "No new manual dump record was created. If FCEUX stayed on the title/opening screen, "
            "this run did not add patch evidence; manually enter the target screen and press D."
        )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

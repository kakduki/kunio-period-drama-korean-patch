#!/usr/bin/env python3
"""Refresh generated reports after a manual FCEUX capture."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from rom_utils import REPO_ROOT


PRIMARY_COMMANDS = [
    [
        "scripts/analyze_manual_screen_dump.py",
        "--input-dir",
        "rom_analysis/manual_screen_dump_v042",
        "--output",
        "rom_analysis/manual_screen_dump_v042/summary.md",
    ],
    ["scripts/generate_manual_capture_status.py"],
    ["scripts/generate_manual_dump_inventory.py"],
    ["scripts/generate_primary_visual_checklist.py"],
    ["scripts/generate_next_manual_run.py"],
    ["scripts/generate_patch_progress_dashboard.py"],
]

BROAD_COMMANDS = [
    ["scripts/analyze_broad_scan_manual_dump.py"],
    ["scripts/generate_route_proof_status.py"],
    ["scripts/generate_v043_proof_status.py"],
    ["scripts/build_v043_from_broad_scan_proof.py"],
    ["scripts/generate_manual_dump_inventory.py"],
    ["scripts/generate_next_manual_run.py"],
    ["scripts/generate_patch_progress_dashboard.py"],
]


NEXT_MANUAL_RUN_JSON = REPO_ROOT / "rom_analysis" / "next_manual_run.json"


def run(args: list[str]) -> None:
    command = [sys.executable, *args]
    print(" ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def command_has_manual_records(args: list[str]) -> bool:
    if not args or args[0] != "scripts/analyze_manual_screen_dump.py":
        return True
    input_dir = REPO_ROOT / "rom_analysis" / "manual_screen_dump"
    if "--input-dir" in args:
        index = args.index("--input-dir") + 1
        input_dir = Path(args[index])
        if not input_dir.is_absolute():
            input_dir = REPO_ROOT / input_dir
    return any(input_dir.glob("manual_frame_*_target_records.tsv"))


def print_next_queue_summary(path=NEXT_MANUAL_RUN_JSON) -> None:
    if not path.exists():
        print(f"next_manual_run_missing={path}")
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    next_action = payload.get("next_action")
    print(
        "next_manual_queue="
        f"actions={summary.get('action_count', 0)} "
        f"primary={summary.get('primary_visual_pending', 0)} "
        f"routes={summary.get('route_proof_pending', 0)}"
    )
    if isinstance(next_action, dict):
        print(
            "next_manual_action="
            f"phase={next_action.get('phase')} "
            f"target={next_action.get('target')} "
            f"group={next_action.get('group')}"
        )
    else:
        print("next_manual_action=none")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=["primary", "broad", "all"],
        default="primary",
        help="Which capture queue was just updated.",
    )
    args = parser.parse_args()

    commands = []
    if args.phase in {"primary", "all"}:
        commands.extend(PRIMARY_COMMANDS)
    if args.phase in {"broad", "all"}:
        commands.extend(BROAD_COMMANDS)

    for command in commands:
        if not command_has_manual_records(command):
            print(f"SKIP no manual target records yet: {' '.join(command)}")
            continue
        run(command)
    print_next_queue_summary()
    print(f"OK: refreshed manual capture reports for phase={args.phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

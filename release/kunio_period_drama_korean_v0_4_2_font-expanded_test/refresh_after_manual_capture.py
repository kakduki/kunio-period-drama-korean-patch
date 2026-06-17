#!/usr/bin/env python3
"""Refresh generated reports after a manual FCEUX capture."""

from __future__ import annotations

import argparse
import subprocess
import sys

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
    ["scripts/generate_primary_visual_checklist.py"],
    ["scripts/generate_next_manual_run.py"],
]

BROAD_COMMANDS = [
    ["scripts/analyze_broad_scan_manual_dump.py"],
    ["scripts/generate_route_proof_status.py"],
    ["scripts/generate_v043_proof_status.py"],
    ["scripts/build_v043_from_broad_scan_proof.py"],
    ["scripts/generate_next_manual_run.py"],
]


def run(args: list[str]) -> None:
    command = [sys.executable, *args]
    print(" ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)


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
        run(command)
    print(f"OK: refreshed manual capture reports for phase={args.phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

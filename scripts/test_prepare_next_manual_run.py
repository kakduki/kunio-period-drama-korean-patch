#!/usr/bin/env python3
"""Check the next manual FCEUX setup helper."""

from __future__ import annotations

import subprocess
import sys

from rom_utils import REPO_ROOT


def main() -> int:
    result = subprocess.run(
        [sys.executable, "scripts/prepare_next_manual_run.py", "--powershell"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out = result.stdout
    required = [
        "Next manual FCEUX capture",
        "Target: 0x07227",
        "Group: Katana",
        "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes",
        "lua\\kunio_manual_v042_capture_watch.lua",
        "python scripts/run_next_manual_fceux.py",
        "does not autoplay through the game",
        "Waiting on the title/opening screen will not create useful patch evidence",
        "python scripts/refresh_after_manual_capture.py --phase primary",
        "python scripts/record_primary_visual_review.py 0x07227 --confirm",
        "If the visible screen matches the target",
        "Press D to save the dump",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"prepare_next_manual_run output missing: {', '.join(missing)}")
    print("OK: next manual run helper prints the focused FCEUX capture setup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

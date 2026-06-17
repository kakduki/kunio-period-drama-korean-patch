#!/usr/bin/env python3
"""Check the manual FCEUX preflight helper."""

from __future__ import annotations

import subprocess
import sys

from rom_utils import REPO_ROOT


def main() -> int:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_manual_fceux.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out = result.stdout
    required = [
        "Manual FCEUX preflight",
        "target: 0x07227 / Katana",
        "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes",
        "lua/kunio_manual_v042_capture_watch.lua",
        "record_primary_visual_review.py 0x07227 --confirm",
        "--stop-after-manual-dump",
        "run_fceux_lua_analysis.py",
        "OK: next manual FCEUX capture inputs are present.",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"manual FCEUX preflight output missing: {', '.join(missing)}")
    print("OK: manual FCEUX preflight validates the next capture setup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

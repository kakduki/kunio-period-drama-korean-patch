#!/usr/bin/env python3
"""Check the next manual FCEUX launcher wrapper."""

from __future__ import annotations

import subprocess
import sys

from rom_utils import REPO_ROOT


def main() -> int:
    result = subprocess.run(
        [sys.executable, "scripts/run_next_manual_fceux.py", "--dry-run"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out = result.stdout
    required = [
        "Next manual FCEUX action: 0x07227 / Katana",
        "press D in FCEUX",
        "scripts/run_fceux_lua_analysis.py",
        "--stop-after-manual-dump",
        "lua/kunio_manual_v042_capture_watch.lua",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"next manual FCEUX wrapper output missing: {', '.join(missing)}")
    print("OK: next manual FCEUX launcher wrapper prints the current action.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

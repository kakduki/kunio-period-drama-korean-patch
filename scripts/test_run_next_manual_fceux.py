#!/usr/bin/env python3
"""Check the next manual FCEUX launcher wrapper."""

from __future__ import annotations

import subprocess
import sys

import run_next_manual_fceux as runner
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
        "Next manual FCEUX action: 0x0569D / Hashi",
        "Required screen: A patched-ROM screen where the Hashi bridge/stage/location label is visibly displayed.",
        "Existing auto-input context: CONTEXT_REJECTED_DIALOGUE_NOT_LOCATION_LABEL",
        "Why existing PNG is not enough",
        "does not autoplay through the game",
        "press D in FCEUX",
        "scripts/run_fceux_lua_analysis.py",
        "--stop-after-manual-dump",
        "lua/kunio_manual_v042_capture_watch.lua",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"next manual FCEUX wrapper output missing: {', '.join(missing)}")
    primary = runner.after_capture_commands(
        {"after_capture": ["python scripts/refresh_after_manual_capture.py --phase primary"]}
    )
    broad = runner.after_capture_commands(
        {"after_capture": ["python scripts/refresh_after_manual_capture.py --phase broad"]}
    )
    if primary != [["scripts/refresh_after_manual_capture.py", "--phase", "primary"]]:
        raise SystemExit("primary after_capture command was not parsed")
    if broad != [["scripts/refresh_after_manual_capture.py", "--phase", "broad"]]:
        raise SystemExit("broad after_capture command was not parsed")
    print("OK: next manual FCEUX launcher wrapper prints the current action.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

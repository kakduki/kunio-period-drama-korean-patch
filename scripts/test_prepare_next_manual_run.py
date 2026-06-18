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
        "Target: 0x0569D",
        "Group: Hashi",
        "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes",
        "lua\\kunio_manual_v042_capture_watch.lua",
        "python scripts/run_next_manual_fceux.py",
        "does not autoplay through the game",
        "Waiting on the title/opening screen will not create useful patch evidence",
        "Required screen: A patched-ROM screen where the Hashi bridge/stage/location label is visibly displayed.",
        "Existing auto-input context: CONTEXT_REJECTED_DIALOGUE_NOT_LOCATION_LABEL",
        "Existing PNG is not enough",
        "After capture if you ran FCEUX/Lua directly instead of the launcher",
        "python scripts/refresh_after_manual_capture.py --phase primary",
        "python scripts/confirm_next_primary_visual.py --confirm-visible",
        "If the visible screen matches the target",
        "Press D to save the dump",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"prepare_next_manual_run output missing: {', '.join(missing)}")
    if "python scripts/record_primary_visual_review.py 0x0569D --confirm" in out:
        raise SystemExit("prepare_next_manual_run should prefer confirm_next_primary_visual for the current primary row")
    print("OK: next manual run helper prints the focused FCEUX capture setup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

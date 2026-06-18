#!/usr/bin/env python3
"""Check the release-gate preflight helper works from the ROM-free bundle."""

from __future__ import annotations

import subprocess
import sys

from rom_utils import REPO_ROOT


BUNDLE_DIR = REPO_ROOT / "release" / "kunio_period_drama_korean_v0_4_2_font-expanded_test"


def main() -> int:
    result = subprocess.run(
        [sys.executable, "preflight_release_gate_action.py"],
        cwd=BUNDLE_DIR,
        text=True,
        capture_output=True,
        check=True,
    )
    out = result.stdout
    required = [
        "Release gate action preflight",
        "mode: bundle",
        "actions: 3",
        "first gate: release-included visual proof",
        "WARNING: release-included visual proof: bundle intentionally omits ROM input",
        "OK: release gate action plan inputs are present.",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"bundle release gate preflight output missing: {', '.join(missing)}")
    print("OK: release gate action preflight works from the ROM-free bundle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check the release gate action preflight helper."""

from __future__ import annotations

import subprocess
import sys

from rom_utils import REPO_ROOT


def main() -> int:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_release_gate_action.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out = result.stdout
    required = [
        "Release gate action preflight",
        "actions: 3",
        "first gate: release-included visual proof",
        "padding v05 strategies: 5",
        "OK: release gate action plan inputs are present.",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"release gate preflight output missing: {', '.join(missing)}")
    print("OK: release gate action preflight validates current evidence task inputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

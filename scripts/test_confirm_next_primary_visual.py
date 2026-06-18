#!/usr/bin/env python3
"""Check the current-next primary visual confirmation helper."""

from __future__ import annotations

import subprocess
import sys

from rom_utils import REPO_ROOT


def main() -> int:
    missing_flag = subprocess.run(
        [sys.executable, "scripts/confirm_next_primary_visual.py", "--dry-run"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert missing_flag.returncode == 1
    assert "--confirm-visible" in missing_flag.stdout

    result = subprocess.run(
        [sys.executable, "scripts/confirm_next_primary_visual.py", "--confirm-visible", "--dry-run"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out = result.stdout
    required = [
        "Confirming primary visual review: 0x0569D / Hashi",
        "Command order: refresh manual dumps, record the visible-screen review, then refresh the queue.",
        "WARNING: no manual dump record is currently indexed",
        "record_primary_visual_review.py 0x0569D --confirm",
        "refresh_after_manual_capture.py --phase primary",
    ]
    missing = [phrase for phrase in required if phrase not in out]
    if missing:
        raise SystemExit(f"confirm-next output missing: {', '.join(missing)}")
    if out.count("refresh_after_manual_capture.py --phase primary") != 2:
        raise SystemExit("confirm-next should refresh before and after recording visual review")
    print("OK: confirm-next primary visual helper is guarded and targets the next row.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

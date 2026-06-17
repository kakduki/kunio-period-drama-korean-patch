#!/usr/bin/env python3
"""Check the helper for recording primary visual review."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from rom_utils import REPO_ROOT


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/record_primary_visual_review.py", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        review = Path(raw_tmp) / "primary_visual_review.json"
        result = run(
            [
                "0x07227",
                "--confirm",
                "--screen-context",
                "katana/weapon item label visible",
                "--visual-review",
                str(review),
            ]
        )
        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(review.read_text(encoding="utf-8"))
        row = next(row for row in payload["rows"] if row["rom_hit"] == "0x07227")
        assert row["visual_context_confirmed"] is True
        assert row["screen_context"] == "katana/weapon item label visible"
        assert row["romaji"] == "Katana"

        result = run(["0x07227", "--clear", "--visual-review", str(review)])
        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(review.read_text(encoding="utf-8"))
        row = next(row for row in payload["rows"] if row["rom_hit"] == "0x07227")
        assert row["visual_context_confirmed"] is False

        result = run(["0x99999", "--confirm", "--visual-review", str(review)])
        assert result.returncode == 1
        assert "not an applied primary patch row" in result.stdout

    print("OK: primary visual review recorder updates a structured review file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

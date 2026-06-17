#!/usr/bin/env python3
"""Check that the progress dashboard is easy to find from project docs."""

from __future__ import annotations

from rom_utils import REPO_ROOT


def assert_contains(path: str, needles: list[str]) -> None:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{path} is missing: {', '.join(missing)}")


def main() -> int:
    assert_contains(
        "README.md",
        [
            "rom_analysis/patch_progress_dashboard.md",
            "current patch status",
            "next FCEUX manual capture target",
        ],
    )
    assert_contains(
        "rom_analysis/README.md",
        [
            "patch_progress_dashboard.md",
            "release blockers",
            "next FCEUX manual action",
        ],
    )
    assert_contains(
        "rom_analysis/patch_progress_dashboard.md",
        [
            "Patch Progress Dashboard",
            "Release Blockers",
            "0x07227",
        ],
    )
    print("OK: patch progress dashboard is linked from the project docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

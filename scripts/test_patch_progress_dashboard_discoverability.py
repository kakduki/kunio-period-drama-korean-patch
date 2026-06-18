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
            "rom_analysis/candidate_pipeline/release_gate_action_plan.md",
            "current patch status",
            "next FCEUX manual capture target",
            "open release gates",
        ],
    )
    assert_contains(
        "rom_analysis/README.md",
        [
            "patch_progress_dashboard.md",
            "candidate_pipeline/release_gate_action_plan.md",
            "release blockers",
            "next FCEUX manual action",
            "concrete evidence tasks",
        ],
    )
    assert_contains(
        "rom_analysis/patch_progress_dashboard.md",
        [
            "Patch Progress Dashboard",
            "Release Blockers",
            "Next gate action",
            "0x0569D",
        ],
    )
    print("OK: patch progress dashboard is linked from the project docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Test the narrow boss-dialogue target generator."""

from __future__ import annotations

from generate_boss_dialogue_targets import build_rows
from rom_utils import REPO_ROOT


def main() -> int:
    rows = build_rows(
        REPO_ROOT / "rom_analysis" / "english_script_dump.tsv",
        REPO_ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv",
    )
    assert len(rows) == 10
    assert [row["pointer_index"] for row in rows] == [
        "020",
        "024",
        "035",
        "077",
        "079",
        "081",
        "101",
        "102",
        "174",
        "188",
    ]
    assert all(row["natural_route_status"] == "UNKNOWN" for row in rows)
    print("OK: boss dialogue target queue contains 10 structural targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

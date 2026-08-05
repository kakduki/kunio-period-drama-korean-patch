#!/usr/bin/env python3
"""Test the complete English-guided pointer dialogue worklist."""

from __future__ import annotations

from build_pointer_dialogue_catalog import (
    POINTER_COUNT,
    POINTER_TABLE_START,
    build_rows,
    load_rows,
)
from rom_utils import REPO_ROOT


def main() -> int:
    english = load_rows(REPO_ROOT / "rom_analysis" / "english_script_dump.tsv")
    conservative = load_rows(REPO_ROOT / "text_data" / "script_catalog.tsv")
    rows = build_rows(english, conservative)
    assert len(rows) == POINTER_COUNT
    assert [int(row["pointer_index"]) for row in rows] == list(range(POINTER_COUNT))
    assert all(
        int(row["pointer_rom_offset"], 16) == POINTER_TABLE_START + int(row["pointer_index"]) * 2
        for row in rows
    )
    assert [row["id"] for row in rows if row["korean_work_status"] == "development_verified_opening"] == [
        *[f"PTR-{index:03d}" for index in range(182, 196)],
    ]
    missing = [row for row in rows if row["conservative_catalog_status"] == "missing"]
    assert len(missing) == 5
    assert all(row["en_length"] == "0" or row["english_reference"] for row in rows)
    print("Complete pointer dialogue catalog tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

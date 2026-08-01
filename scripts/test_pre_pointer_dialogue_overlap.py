#!/usr/bin/env python3
"""Verify the pre-pointer dialogue ownership audit report."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


REPORT = REPO_ROOT / "rom_analysis" / "pre_pointer_dialogue_overlap.json"


def main() -> int:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    assert payload["inventory_rows"] == 250
    assert payload["english_dialogue_owner_runs"] == 722
    assert payload["overlap_summary"] == {
        "EDGE_OVERLAP": 25,
        "FULLY_CONTAINED": 161,
        "NO_OVERLAP": 35,
        "RUN_INSIDE_ROW": 29,
    }
    assert len(payload["fully_contained_runtime_candidates"]) == 10
    assert "EN-PRE-138" in payload["fully_contained_runtime_candidates"]
    print("PASS pre-pointer dialogue ownership audit")
    print("inventory_rows=250")
    print("english_dialogue_owner_runs=722")
    print("fully_contained_runtime_candidates=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

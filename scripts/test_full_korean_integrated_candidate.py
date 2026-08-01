#!/usr/bin/env python3
"""Regression test for the integrated candidate runtime report."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


REPORT = REPO_ROOT / "rom_analysis" / "full_korean_integrated_runtime.json"


def main() -> int:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_INTEGRATED_BOOT_RUNTIME_NOT_READY"
    assert payload["release_status"] == "NOT_READY"
    assert payload["pre_pointer"]["matched_rows"] == 10
    assert payload["pre_pointer"]["lua_done"] is True
    assert payload["stage_progression"]["lua_done"] is True
    assert payload["stage_progression"]["combat_frames"]
    assert payload["stage_progression"]["boss_proof"] is False
    print("PASS integrated candidate runtime report")
    print("pre_pointer_exact_owner=10/10")
    print("stage_progression=lua_done")
    print("boss_proof=NOT_AVAILABLE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

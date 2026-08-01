#!/usr/bin/env python3
"""Regression test for the 22-row expanded candidate evidence."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


BUILD_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_expanded_candidate.json"
RUNTIME_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_expanded_runtime.json"


def main() -> int:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_REPORT.read_text(encoding="utf-8"))
    assert build["target_count"] == 22
    assert len(build["glyph_codes"]) == 26
    assert build["candidate_md5"] == runtime["candidate_md5"]
    assert runtime["status"] == "PASS_INTEGRATED_BOOT_RUNTIME_NOT_READY"
    assert runtime["pre_pointer"]["matched_rows"] == 22
    assert runtime["stage_progression"]["lua_done"] is True
    assert runtime["stage_progression"]["combat_frames"]
    assert runtime["stage_progression"]["boss_proof"] is False
    print("PASS expanded integrated candidate")
    print("fixed_label_exact_owner=22/22")
    print("glyph_codes=26")
    print("release_status=NOT_READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

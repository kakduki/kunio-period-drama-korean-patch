#!/usr/bin/env python3
"""Regression test for the composed Korean candidate and its runtime evidence."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


BUILD_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_full_composed_expanded_candidate.json"
RUNTIME_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_full_composed_expanded_runtime.json"
ITEMS_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_full_composed_expanded_items_runtime.json"


def main() -> int:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_REPORT.read_text(encoding="utf-8"))
    items = json.loads(ITEMS_REPORT.read_text(encoding="utf-8"))

    assert build["input_md5"] == "5f348772bb6809b1df0e7f84ef2e7603"
    assert build["reference_structure_applied"] is False
    assert build["target_count"] == 22
    assert len(build["glyph_codes"]) == 26
    assert build["candidate_md5"] == runtime["candidate_md5"]
    assert runtime["status"] == "PASS_INTEGRATED_BOOT_RUNTIME_NOT_READY"
    assert runtime["pre_pointer"]["matched_rows"] == 22
    assert runtime["stage_progression"]["lua_done"] is True
    assert runtime["stage_progression"]["unique_screens"] >= 2
    assert runtime["stage_progression"]["combat_frames"]
    assert runtime["stage_progression"]["boss_proof"] is False
    assert items["source_bytes_pass"] is True
    assert items["queue_title_none_pass"] is True
    assert items["runtime_byte_gate"] is True
    print("PASS composed full Korean candidate")
    print("fixed_label_exact_owner=22/22")
    print("glyph_codes=26")
    print("items_title_none_byte_gate=PASS")
    print("release_status=NOT_READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

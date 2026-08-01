#!/usr/bin/env python3
"""Verify the bounded full-candidate composition and runtime evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT


CANDIDATE = REPO_ROOT / "output" / "full_korean_items_title_none_nonpointer_candidate" / "kunio_period_drama_korean_expanded_nonpointer_candidate.nes"
REPORT = REPO_ROOT / "rom_analysis" / "full_korean_composed_candidate.md"
ITEMS_RUNTIME = REPO_ROOT / "rom_analysis" / "items_title_none_compatible_runtime.json"
EXPLORER = REPO_ROOT / "rom_analysis" / "full_composed_input_explorer"
NONPOINTER_JSON = REPO_ROOT / "rom_analysis" / "full_korean_items_title_none_nonpointer_candidate.json"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main() -> int:
    assert CANDIDATE.exists(), CANDIDATE
    assert REPORT.exists(), REPORT
    assert md5(CANDIDATE) == "5f348772bb6809b1df0e7f84ef2e7603"

    nonpointer = json.loads(NONPOINTER_JSON.read_text(encoding="utf-8"))
    assert nonpointer["selected_target_count"] == 8
    assert nonpointer["skipped_offsets"] == ["0x0561A"]
    assert nonpointer["glyph_slot_count"] == 18
    assert nonpointer["ips_records"] == 28

    items = json.loads(ITEMS_RUNTIME.read_text(encoding="utf-8"))
    assert items["source_bytes_pass"] is True
    assert items["queue_title_none_pass"] is True
    assert items["runtime_byte_gate"] is True

    summary = (EXPLORER / "explorer_summary.tsv").read_text(encoding="utf-8-sig")
    assert "\t362\t" not in summary
    assert "361\tstart_a_menu" in summary
    assert "1146\tstart_select_inventory" in summary
    assert "1200\tdone\t" in summary

    target_rows = (EXPLORER / "manual_frame_000362_target_records.tsv").read_text(encoding="utf-8-sig")
    active = [line for line in target_rows.splitlines()[1:] if line.split("\t")[6].lower() == "true"]
    assert len(active) == 8, len(active)
    assert any("ROM+0x0561A" in line and line.split("\t")[6].lower() == "false" for line in target_rows.splitlines()[1:])

    print("PASS full composed candidate static/runtime evidence")
    print("candidate_md5=5f348772bb6809b1df0e7f84ef2e7603")
    print("items_runtime=PASS_BYTE_PROOF_VISUAL_UNKNOWN")
    print("frame_362_active_nonpointer_targets=8/9")
    print("frame_1200=done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

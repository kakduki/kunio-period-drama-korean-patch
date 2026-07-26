#!/usr/bin/env python3
"""Test MMC3 mapping reconstruction without launching FCEUX."""

from __future__ import annotations

import tempfile
from pathlib import Path

from analyze_opening_mapper_trace import analyze, resolve_chr_windows


def write_trace(root: Path, *, complete: bool) -> None:
    (root / "summary.tsv").write_text(
        "frame\treason\tdetail_a\tdetail_b\tdetail_c\n"
        "0\tlua_start\tcapture_frame=883\tmax_frames=920\tmapper_callbacks=true\n"
        "883\tlua_done\tcaptured=true\tmapper_data_callbacks=6\tppu_control_callbacks=1\n",
        encoding="utf-8",
    )
    registers = "38\t3A\t3C\t3D\t3E\t3F\t\t"
    if not complete:
        registers = "38\t\t3C\t3D\t3E\t3F\t\t"
    (root / "mapper_snapshot.tsv").write_text(
        "frame\tmapper_control\tmapper_select\tppu_control\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tmapper_select_callbacks\tmapper_data_callbacks\tppu_control_callbacks\n"
        f"883\t00\t4\t10\t{registers}6\t6\t1\n",
        encoding="utf-8",
    )
    (root / "mapper_writes.tsv").write_text(
        "frame\tkind\tvalue\tselected_register\tpc\n"
        "880\tMMC3_SELECT\t04\t4\tC123\n"
        "880\tMMC3_DATA\t3E\t4\tC125\n"
        "881\tMMC3_SELECT\t04\t4\tC123\n"
        "881\tMMC3_DATA\t3E\t4\tC125\n"
        "881\tPPUCTRL\t10\t\tC200\n",
        encoding="utf-8",
    )


def check_mode_mapping() -> None:
    assert resolve_chr_windows(0x00, [0x38, 0x3A, 0x3C, 0x3D, 0x3E, 0x3F]) == [
        0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F
    ]
    assert resolve_chr_windows(0x80, [0x38, 0x3A, 0x3C, 0x3D, 0x3E, 0x3F]) == [
        0x3C, 0x3D, 0x3E, 0x3F, 0x38, 0x39, 0x3A, 0x3B
    ]


def check_complete_trace() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp)
        write_trace(root, complete=True)
        payload = analyze(root)
    assert payload["overall_verdict"] == "PASS"
    assert payload["background_pattern_base"] == "0x1000"
    assert payload["expected_reference_slots_match"] is True
    first = payload["reference_code_mappings"][0]
    assert first["code"] == "0x81"
    assert first["physical_chr_8k_bank"] == 7
    assert first["physical_tile_in_bank"] == "0x181"
    assert payload["recurring_write_pcs"]["mmc3_select"] == [
        {"pc": "0xC123", "writes": 2}
    ]


def check_expected_page_override() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp)
        write_trace(root, complete=True)
        payload = analyze(root, expected_physical_chr_bank=8)
    assert payload["expected_physical_chr_8k_bank"] == 8
    assert payload["expected_reference_slots_match"] is False


def check_incomplete_trace_is_unknown() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp)
        write_trace(root, complete=False)
        payload = analyze(root)
    assert payload["overall_verdict"] == "UNKNOWN"
    assert payload["missing"]["chr_registers"] == ["r1"]


def main() -> int:
    check_mode_mapping()
    check_complete_trace()
    check_expected_page_override()
    check_incomplete_trace_is_unknown()
    print("Opening MMC3 mapper trace analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

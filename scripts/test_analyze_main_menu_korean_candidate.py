#!/usr/bin/env python3
"""Synthetic positive-path coverage for the main-menu candidate smoke analyzer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from analyze_main_menu_korean_candidate import analyze
from analyze_reference_ips import parse_ines_layout
from build_main_menu_korean_candidate import (
    CHR_PAIR_SIZE,
    CLONE_CHR_1K_PAIR,
    RASTER_R1_VALUE_CLONE,
    RASTER_R1_VALUE_ORIGINAL,
    RASTER_R1_VALUE_ROM_OFFSET,
    SOURCE_CHR_1K_PAIR,
    TEMPLATE_LENGTH,
    TEMPLATE_ROM_OFFSET,
    build_menu_template,
    chr_page_offset,
)


def synthetic_base() -> bytearray:
    data = bytearray(0x40010)
    data[:4] = b"NES\x1a"
    data[4] = 8
    data[5] = 16
    data[RASTER_R1_VALUE_ROM_OFFSET] = RASTER_R1_VALUE_ORIGINAL
    return data


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        base = synthetic_base()
        base_path = root / "base.nes"
        base_path.write_bytes(base)
        template = build_menu_template(base)
        layout = parse_ines_layout(base)
        source_start = chr_page_offset(layout, SOURCE_CHR_1K_PAIR)
        clone_start = chr_page_offset(layout, CLONE_CHR_1K_PAIR)
        candidate = bytearray(base)
        candidate[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH] = template
        candidate[clone_start : clone_start + CHR_PAIR_SIZE] = base[
            source_start : source_start + CHR_PAIR_SIZE
        ]
        candidate[clone_start] = 1
        candidate[RASTER_R1_VALUE_ROM_OFFSET] = RASTER_R1_VALUE_CLONE
        candidate_path = root / "candidate.nes"
        candidate_path.write_bytes(candidate)

        capture = root / "capture"
        capture.mkdir()
        (capture / "summary.tsv").write_text(
            "frame\treason\n0\tlua_start\n1906\tlua_done\n",
            encoding="utf-8",
        )
        (capture / "mapper_snapshot.tsv").write_text(
            "frame\tmapper_control\tmapper_select\tppu_control\tr0\tr1\n"
            "1906\t07\t7\t88\t3C\t46\n",
            encoding="utf-8",
        )
        (capture / "mapper_config_writes.tsv").write_text(
            "frame\taddress\tvalue\tpc\n1906\t0503\t46\tEE51\n",
            encoding="utf-8",
        )
        nametables = bytearray(0x1000)
        nametables[0x700 : 0x700 + TEMPLATE_LENGTH] = template
        nametables[0xF00 : 0xF00 + TEMPLATE_LENGTH] = template
        (capture / "main_menu_frame_001906_nametables_2000_2fff.bin").write_bytes(nametables)
        (capture / "main_menu_frame_001906_screen.png").write_bytes(b"screen-evidence")

        payload = analyze(
            base_rom_path=base_path,
            candidate_rom_path=candidate_path,
            capture_dir=capture,
        )

    assert payload["status"] == "SOFT_GATE_PASS"
    assert payload["release_verdict"] == "UNKNOWN"
    assert all(payload["checks"].values())
    print("Main-menu Korean candidate smoke analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

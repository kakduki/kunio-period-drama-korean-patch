#!/usr/bin/env python3
"""Focused tests for the fixed main-menu template/context analyzer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from analyze_main_menu_context import (
    DISPLAY_TEMPLATE_OFFSET,
    EXPECTED_ENGLISH_LABELS,
    TEMPLATE_LENGTH,
    TEMPLATE_ROM_OFFSET,
    analyze,
)


def template(*labels: bytes) -> bytes:
    data = bytearray(TEMPLATE_LENGTH)
    slots = ((25, 2), (25, 9), (25, 16), (25, 23), (27, 2), (27, 9), (27, 16), (27, 23))
    for (row, column), value in zip(slots, labels, strict=True):
        offset = (row - 24) * 32 + column
        data[offset : offset + len(value)] = value
    return bytes(data)


def write_capture(root: Path, data: bytes) -> None:
    root.mkdir(parents=True)
    (root / "summary.tsv").write_text(
        "frame\treason\n0\tlua_start\n1906\tlua_done\n", encoding="utf-8"
    )
    nametables = bytearray(0x1000)
    nametables[DISPLAY_TEMPLATE_OFFSET : DISPLAY_TEMPLATE_OFFSET + TEMPLATE_LENGTH] = data
    nametables[0xF00 : 0xF00 + TEMPLATE_LENGTH] = data
    (root / "main_menu_frame_001906_nametables_2000_2fff.bin").write_bytes(nametables)
    (root / "mapper_snapshot.tsv").write_text(
        "frame\tmapper_control\tmapper_select\tppu_control\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\n"
        "1906\t07\t7\t88\t3C\t3E\t42\t47\t35\t40\t0C\t0D\n",
        encoding="utf-8",
    )


def main() -> int:
    base_template = template(
        bytes.fromhex("A3 91 A3 99"),
        bytes.fromhex("8D 93 71 90 8D"),
        bytes.fromhex("AC A8 9C A8"),
        bytes.fromhex("9B B4 8B 92 AC 8B"),
        bytes.fromhex("87 AB 88"),
        bytes.fromhex("8B 88 8E AE"),
        bytes.fromhex("8E B4 93 82"),
        bytes.fromhex("89 71 A1 A3 71 94"),
    )
    reference_template = template(
        b"\x89\x94\x85\x8D\x93",
        b"\x93\x94\x81\x94\x95\x93",
        b"\x87\x92\x8F\x97\x94\x88",
        b"\x94\x85\x83\x88",
        b"\x93\x81\x96\x85",
        b"\x81\x8C\x8C\x99",
        b"\x93\x85\x94\x94\x8E\x87",
        b"\x93\x85\x94\x95\x90",
    )
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        base_rom = bytearray(TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH)
        reference_rom = bytearray(base_rom)
        base_rom[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH] = base_template
        reference_rom[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH] = reference_template
        base_path = root / "base.nes"
        reference_path = root / "reference.nes"
        base_path.write_bytes(base_rom)
        reference_path.write_bytes(reference_rom)
        base_capture = root / "base_capture"
        reference_capture = root / "reference_capture"
        write_capture(base_capture, base_template)
        write_capture(reference_capture, reference_template)
        payload = analyze(
            base_rom_path=base_path,
            reference_rom_path=reference_path,
            base_capture_dir=base_capture,
            reference_capture_dir=reference_capture,
        )

    assert payload["overall_verdict"] == "PASS"
    assert payload["checks"]["base_template_matches_display"]
    assert payload["checks"]["reference_template_matches_display"]
    assert payload["checks"]["base_mapper_resolves_visible_label_page"]
    assert payload["visible_label_mapper_mapping"]["visible_chr_1k_page"] == "0x3E"
    assert [row["english_reference"] for row in payload["labels"]] == list(EXPECTED_ENGLISH_LABELS)
    assert payload["readability_layout"][0]["top_row"] == 24
    assert payload["readability_layout"][4]["top_row"] == 26
    print("Main-menu context analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

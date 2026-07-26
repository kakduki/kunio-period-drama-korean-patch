#!/usr/bin/env python3
"""Focused tests for the physical English-reference CHR slot mapper."""

from __future__ import annotations

from analyze_english_font_slots import analyze_font_slots


def make_rom() -> bytes:
    rom = bytearray(16 + 0x4000 + 0x2000)
    rom[:4] = b"NES\x1a"
    rom[4] = 1
    rom[5] = 1
    return bytes(rom)


def main() -> int:
    base = make_rom()
    reference = bytearray(base)
    chr_start = 16 + 0x4000
    reference[chr_start + 0x181 * 16] = 0x80
    reference[chr_start + 0x19A * 16 + 15] = 0x01
    reference[chr_start + 0x180 * 16 + 4] = 0xFF

    payload = analyze_font_slots(base, bytes(reference))
    bank = payload["changed_chr_banks"][0]
    assert bank["chr_bank"] == 0
    assert bank["changed_tile_count"] == 3
    assert bank["changed_tile_spans"] == ["0x180-0x181", "0x19A"]

    coverage = payload["english_letter_code_coverage"]
    a_row = next(row for row in coverage if row["code"] == "0x81")
    z_row = next(row for row in coverage if row["code"] == "0x9A")
    assert a_row["physical_slot_count"] == 1
    assert z_row["physical_slot_count"] == 1
    assert a_row["english_letter"] == "A"
    assert z_row["english_letter"] == "Z"
    print("English reference font slot mapper tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

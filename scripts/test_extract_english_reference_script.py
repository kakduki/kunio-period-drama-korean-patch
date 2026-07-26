#!/usr/bin/env python3
"""Focused regression tests for the English reference script extractor."""

from __future__ import annotations

from extract_english_reference_script import (
    CPU_BANK_START,
    PointerEntry,
    decode_english_dialogue,
    decode_japanese_dialogue,
    excerpt_end,
    parse_pointer_table,
    split_ff_records,
    target_scope,
    target_windows,
)


def test_pointer_table_stops_at_first_non_cpu_word() -> None:
    data = bytearray(0x100)
    data[0x10:0x12] = (0x8010).to_bytes(2, "little")
    data[0x12:0x14] = (0x8020).to_bytes(2, "little")
    data[0x14:0x16] = (0x007F).to_bytes(2, "little")

    entries, end = parse_pointer_table(data, 0x10, 0x40, 0x80)

    assert end == 0x14
    assert [entry.cpu_address for entry in entries] == [0x8010, 0x8020]
    assert [entry.target_rom_offset for entry in entries] == [0x50, 0x60]
    assert all(entry.target_in_bank for entry in entries)


def test_dialogue_decoders_preserve_unknown_control_bytes() -> None:
    assert decode_english_dialogue(bytes([0x81, 0x80, 0x9A, 0xFF])) == "A Z<FF>"
    assert decode_japanese_dialogue(bytes([0x81, 0xAF, 0x9F, 0xFF])) == "<81><AF><9F><FF>"


def test_delimiter_records_keep_empty_records_and_tail() -> None:
    records = split_ff_records(bytes([0x81, 0xFF, 0xFF, 0x82]), 0, 4)

    assert [(row.start, row.end_exclusive, row.has_ff_delimiter) for row in records] == [
        (0, 2, True),
        (2, 3, True),
        (3, 4, False),
    ]
    assert [row.data for row in records] == [b"\x81\xff", b"\xff", b"\x82"]


def test_target_windows_and_shared_delimiter_excerpt() -> None:
    data = bytes([0xFF, 0x81, 0xFF, 0x82])
    assert excerpt_end(data, 0, 4) == 3

    entries = [
        PointerEntry(0, 0, 0x8010, CPU_BANK_START + 0x10, True),
        PointerEntry(1, 2, 0x8020, CPU_BANK_START + 0x20, True),
        PointerEntry(2, 4, 0x8020, CPU_BANK_START + 0x20, True),
    ]
    windows = target_windows(entries, CPU_BANK_START + 0x10, CPU_BANK_START + 0x30)
    assert windows == {
        CPU_BANK_START + 0x10: CPU_BANK_START + 0x20,
        CPU_BANK_START + 0x20: CPU_BANK_START + 0x30,
    }
    assert (
        target_scope(0x4010, 0x5DD4, 0x5FC4, 0x8010)
        == "bank1_before_pointer_table"
    )


def main() -> int:
    test_pointer_table_stops_at_first_non_cpu_word()
    test_dialogue_decoders_preserve_unknown_control_bytes()
    test_delimiter_records_keep_empty_records_and_tail()
    test_target_windows_and_shared_delimiter_excerpt()
    print("English reference script extractor tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

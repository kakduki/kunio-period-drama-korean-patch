#!/usr/bin/env python3
"""Focused tests for static dialogue-renderer evidence extraction."""

from __future__ import annotations

from analyze_dialogue_renderer import (
    CONTROL_PREFIX,
    cpu_address_to_bank_file_offset,
    extract_control_codes,
)


def test_extract_control_codes() -> None:
    data = (
        b"\x00" * 4
        + CONTROL_PREFIX
        + bytes.fromhex(
            "8A F0 20 C9 8B F0 1C C9 AC F0 18 "
            "C9 B0 F0 14 C9 BB F0 10 C9 FA F0 0C"
        )
        + b"\xA6"
    )
    offset, codes = extract_control_codes(data, 0, len(data))

    assert offset == 4
    assert codes == [0x8A, 0x8B, 0xAC, 0xB0, 0xBB, 0xFA]


def test_cpu_address_maps_inside_parser_bank() -> None:
    assert cpu_address_to_bank_file_offset(0x829E, 0x8010, 0xC010) == 0x82AE


def main() -> int:
    test_extract_control_codes()
    test_cpu_address_maps_inside_parser_bank()
    print("Dialogue renderer analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

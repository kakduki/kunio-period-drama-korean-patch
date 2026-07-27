#!/usr/bin/env python3
"""Test the direct 8x16 pointer-dialogue candidate invariants."""

from __future__ import annotations

from build_opening_dialogue_16x16_proof import (
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
)
from build_pointer_dialogue_8x16_candidate import apply_candidate


def make_fixture() -> bytes:
    rom = bytearray(16 + 0x20000 + 0x20000)
    rom[:4] = b"NES\x1a"
    rom[4] = 8
    rom[5] = 16
    for index, cpu in enumerate((0x9FD7, 0x9FF9, 0xA004, 0xA012), 0):
        offset = 0x05DD4 + index * 2
        rom[offset:offset + 2] = cpu.to_bytes(2, "little")
    rom[0x05FE7:0x05FE7 + 34] = bytes([0xA5]) * 34
    rom[0x06009:0x06009 + 11] = bytes([0xA6]) * 11
    rom[0x06014:0x06014 + 14] = bytes([0xA7]) * 14
    rom[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] = RENDER_ENTRY_ORIGINAL
    rom[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] = RENDER_MARKER_ORIGINAL
    rom[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] = b"\xff" * CODE_CAVE_SIZE
    return bytes(rom)


def main() -> int:
    base = make_fixture()
    config = {
        "glyph_codes": {"가": 0x81, "나": 0x82},
        "records": [
            {
                "pointer_index": 0,
                "pointer_rom_offset": 0x05DD4,
                "record_rom_offset": 0x05FE7,
                "old_pointer_cpu": 0x9FD7,
                "new_pointer_cpu": 0x9FD7,
                "encoded": bytes.fromhex("F0 BB 00 81 82 CA FF"),
            },
            {
                "pointer_index": 1,
                "pointer_rom_offset": 0x05DD6,
                "record_rom_offset": 0x05FEE,
                "old_pointer_cpu": 0x9FF9,
                "new_pointer_cpu": 0x9FDE,
                "encoded": bytes.fromhex("F0 BB 00 82 CA FF"),
            },
        ],
    }
    glyph_tiles = {
        "가": (bytes([0x11]) * 16, bytes([0x22]) * 16),
        "나": (bytes([0x33]) * 16, bytes([0x44]) * 16),
    }
    patched, targets, helper = apply_candidate(base, config, glyph_tiles)
    assert patched[0x05FE7:0x05FEE] == config["records"][0]["encoded"]
    assert patched[0x05FEE:0x05FF4] == config["records"][1]["encoded"]
    assert int.from_bytes(patched[0x05DD6:0x05DD8], "little") == 0x9FDE
    assert helper.record_cpu_addresses == (0x9FD7, 0x9FDE)
    assert helper.accepts_source_code(0x81)
    assert helper.accepts_source_code(0x82)
    assert not helper.accepts_source_code(0xBB)
    assert any(target["kind"] == "font_tile_bottom" for target in targets)
    assert any(target["kind"] == "dialogue_pointer" for target in targets)
    print("Pointer dialogue direct 8x16 candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

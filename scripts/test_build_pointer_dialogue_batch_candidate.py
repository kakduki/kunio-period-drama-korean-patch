#!/usr/bin/env python3
"""Test the multi-record pointer-dialogue candidate invariants."""

from __future__ import annotations

from pathlib import Path

from build_opening_dialogue_16x16_proof import (
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
)
from build_pointer_dialogue_batch_candidate import apply_candidate, validate_catalog


def make_fixture() -> bytes:
    rom = bytearray(16 + 0x20000 + 0x20000)
    rom[:4] = b"NES\x1a"
    rom[4] = 8
    rom[5] = 16
    rom[0x05DD8:0x05DDA] = (0xA004).to_bytes(2, "little")
    rom[0x05DDA:0x05DDC] = (0xA012).to_bytes(2, "little")
    rom[0x05DDC:0x05DDE] = (0xA044).to_bytes(2, "little")
    rom[0x06014:0x06014 + 14] = bytes.fromhex("F0 BB 9F 90 00 81 82 8C A4 8C 90 98 CD FF")
    rom[0x06022:0x06022 + 50] = bytes.fromhex("F0 BB 8F 85 82 A4 AF 00 A0 B7 83 95 9C 90 A8 08 A0 06 82 A4 8C 90 98 F8 F9 00 85 A2 B2 8B AE 06 00 8B 06 8C 93 A9 A4 92 A7 96 00 91 09 B2 98 B2 A6 FF")
    rom[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] = RENDER_ENTRY_ORIGINAL
    rom[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] = RENDER_MARKER_ORIGINAL
    rom[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] = b"\xff" * CODE_CAVE_SIZE
    return bytes(rom)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalog = root / "text_data" / "korean_scene_batches" / "pointer_dialogue_ptr_002_003.json"
    base = make_fixture()
    config = validate_catalog(catalog, base)
    pairs = config["glyph_code_pairs"]
    assert isinstance(pairs, dict)
    glyph_tiles = {glyph: (bytes([index]) * 16, bytes([index + 1]) * 16, bytes([index + 2]) * 16, bytes([index + 3]) * 16) for index, glyph in enumerate(pairs, 1)}
    patched, targets, helper = apply_candidate(base, config, glyph_tiles)
    records = config["records"]
    assert isinstance(records, list)
    assert patched[0x06014:0x06014 + len(records[0]["encoded"])] == records[0]["encoded"]
    assert patched[0x06021:0x06021 + len(records[1]["encoded"])] == records[1]["encoded"]
    assert int.from_bytes(patched[0x05DDA:0x05DDC], "little") == 0xA011
    assert int.from_bytes(patched[0x05DDC:0x05DDE], "little") == 0xA044
    assert helper.record_cpu_addresses == (0xA004, 0xA011)
    assert helper.accepts_source_code(0x81)
    assert helper.accepts_source_code(0xC3)
    assert not helper.accepts_source_code(0xBB)
    assert not helper.accepts_source_code(0xCA)
    assert any(target["kind"] == "dialogue_pointer" for target in targets)
    print("Pointer dialogue batch candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

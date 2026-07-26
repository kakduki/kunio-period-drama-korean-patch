#!/usr/bin/env python3
"""Focused invariants for the range-scoped three-record opening candidate."""

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
from build_opening_dialogue_182_183_16x16 import (
    apply_candidate,
    pointer_cpu,
    pointer_indices_in_range,
    validate_catalog,
)
from build_opening_dialogue_proof import ORIGINAL_RECORD, RECORD_ROM_OFFSET


PTR_183_BASE_RECORD = bytes.fromhex(
    "85 8A 94 BB 88 96 9F 8B 8B AE CA 85 9F 91 8C 93 9F 8C 90 CA FF"
)
PTR_184_BASE_RECORD = bytes.fromhex(
    "88 96 9F 8B BB 85 8A 94 8B AE CB F8 F9 00 85 9B 8B 8C 1C A8 13 B2 CA FF"
)


def make_fixture() -> bytes:
    rom = bytearray(16 + 0x20000 + 0x20000)
    rom[:4] = b"NES\x1a"
    rom[4] = 8
    rom[5] = 16
    rom[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + len(ORIGINAL_RECORD)] = ORIGINAL_RECORD
    rom[0x071DB:0x071DB + len(PTR_183_BASE_RECORD)] = PTR_183_BASE_RECORD
    rom[0x071F0:0x071F0 + len(PTR_184_BASE_RECORD)] = PTR_184_BASE_RECORD
    rom[0x05F40:0x05F42] = (0xB1A6).to_bytes(2, "little")
    rom[0x05F42:0x05F44] = (0xB1CB).to_bytes(2, "little")
    rom[0x05F44:0x05F46] = (0xB1E0).to_bytes(2, "little")
    rom[0x05F46:0x05F48] = (0xB1F8).to_bytes(2, "little")
    rom[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] = RENDER_ENTRY_ORIGINAL
    rom[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] = RENDER_MARKER_ORIGINAL
    rom[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] = b"\xff" * CODE_CAVE_SIZE
    return bytes(rom)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    config = validate_catalog(
        root / "text_data" / "korean_scene_batches" / "opening_ptr_182_184_16x16_readability.json"
    )
    pairs = config["glyph_code_pairs"]
    encoded_records = config["encoded_records"]
    assert isinstance(pairs, dict) and isinstance(encoded_records, list)
    glyphs = {
        glyph: tuple(bytes((index + part,)) * 16 for part in range(1, 5))
        for index, glyph in enumerate(pairs)
    }

    patched, targets, helper = apply_candidate(make_fixture(), glyphs, config)
    first, second, third = encoded_records
    assert patched[0x071B6:0x071B6 + len(first)] == first
    assert patched[0x071D6:0x071D6 + len(second)] == second
    assert patched[0x071EF:0x071EF + len(third)] == third
    assert pointer_cpu(patched, 182) == 0xB1A6
    assert pointer_cpu(patched, 183) == 0xB1C6
    assert pointer_cpu(patched, 184) == 0xB1DF
    assert pointer_cpu(patched, 185) == 0xB1F8
    assert pointer_indices_in_range(patched, 0xB1A6, 0xB1E0) == [182, 183, 184]
    assert helper.record_cpu_addresses == ()
    assert helper.record_cpu_range == (0xB1A6, 0xB1E0)
    assert helper.accepts_source_code(0x9F)
    assert helper.accepts_source_code(0xC8)
    assert not helper.accepts_source_code(0xBB)
    assert not helper.accepts_source_code(0xCA)
    assert len(helper.code) <= CODE_CAVE_SIZE
    assert sum(target["kind"] == "dialogue_pointer" for target in targets) == 2
    print("Three-record range-scoped opening Korean 16x16 candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

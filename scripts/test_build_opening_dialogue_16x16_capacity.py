#!/usr/bin/env python3
"""Focused tests for catalog-driven paired 16x16 capacity candidates."""

from __future__ import annotations

from pathlib import Path

from build_opening_dialogue_16x16_capacity import (
    apply_capacity_candidate,
    validate_capacity_catalog,
)
from build_opening_dialogue_8x16_proof import CODE_CAVE_CPU
from build_opening_dialogue_16x16_proof import (
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    ENTRY_HOOK,
    MARKER_HOOK,
    ORIGINAL_RECORD,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
    helper_code_for_range,
)


NEIGHBOR_POINTER_ROM_OFFSET = 0x05F42
NEIGHBOR_RECORD_ROM_OFFSET = 0x071DB
NEIGHBOR_RECORD = bytes.fromhex("85 8A 94 BB 88 96 9F 8B 8B AE CA 85 9F 91 8C 93 9F 8C 90 CA FF")


def make_fixture() -> bytes:
    rom = bytearray(16 + 0x20000 + 0x20000)
    rom[:4] = b"NES\x1a"
    rom[4] = 8
    rom[5] = 16
    rom[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = ORIGINAL_RECORD
    rom[0x05F40:0x05F42] = (0xB1A6).to_bytes(2, "little")
    rom[NEIGHBOR_POINTER_ROM_OFFSET:NEIGHBOR_POINTER_ROM_OFFSET + 2] = (0xB1CB).to_bytes(2, "little")
    rom[NEIGHBOR_RECORD_ROM_OFFSET:NEIGHBOR_RECORD_ROM_OFFSET + len(NEIGHBOR_RECORD)] = NEIGHBOR_RECORD
    rom[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] = RENDER_ENTRY_ORIGINAL
    rom[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] = RENDER_MARKER_ORIGINAL
    rom[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] = b"\xff" * CODE_CAVE_SIZE
    return bytes(rom)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalogs = (
        ("opening_ptr_182_16x16_capacity_tier1.json", tuple(range(0x81, 0x9B)), 13, 37, False),
        (
            "opening_ptr_182_16x16_capacity_tier2.json",
            tuple(range(0x81, 0x9B)) + tuple(range(0xC0, 0xC8)),
            17,
            37,
            False,
        ),
        (
            "opening_ptr_182_16x16_relocation_proof.json",
            tuple(range(0x81, 0x9B)) + (0xC4, 0xC5, 0xC0, 0xC1, 0xC2, 0xC3, 0xC6, 0xC7),
            17,
            45,
            True,
        ),
    )
    for filename, expected_codes, expected_glyph_count, expected_length, expects_relocation in catalogs:
        config = validate_capacity_catalog(root / "text_data" / "korean_scene_batches" / filename)
        profile = config["profile"]
        assert isinstance(profile, dict)
        pairs = profile["glyph_code_pairs"]
        source_codes = profile["source_codes"]
        assert isinstance(pairs, dict) and isinstance(source_codes, tuple)
        assert source_codes == expected_codes
        assert len(pairs) == expected_glyph_count
        assert len(config["encoded"]) == expected_length

        glyphs = {
            glyph: tuple(bytes([index + part]) * 16 for part in range(1, 5))
            for index, glyph in enumerate(pairs)
        }
        patched, targets = apply_capacity_candidate(make_fixture(), glyphs, config)
        assert patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + expected_length] == config["encoded"]
        assert patched[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + 3] == ENTRY_HOOK
        assert patched[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + 3] == MARKER_HOOK
        font_targets = [target for target in targets if str(target["kind"]).startswith("font_tile_")]
        assert len(font_targets) == len(pairs) * 4
        assert {int(str(target["code"]), 16) for target in font_targets} == {
            code for code in source_codes
        } | {code + 0x20 for code in source_codes}
        if expects_relocation:
            helper = helper_code_for_range(start_code=0x81, end_code_exclusive=0xC8)
            relocated_rom_offset = CODE_CAVE_ROM_OFFSET + len(helper)
            assert patched[NEIGHBOR_POINTER_ROM_OFFSET:NEIGHBOR_POINTER_ROM_OFFSET + 2] == (
                CODE_CAVE_CPU + len(helper)
            ).to_bytes(2, "little")
            assert patched[relocated_rom_offset:relocated_rom_offset + len(NEIGHBOR_RECORD)] == NEIGHBOR_RECORD
            assert any(target["kind"] == "relocated_neighbor_pointer" for target in targets)
            assert any(target["kind"] == "relocated_neighbor_record" for target in targets)
    print("Opening dialogue catalog-driven paired 16x16 capacity tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

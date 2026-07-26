#!/usr/bin/env python3
"""Focused tests for the paired-8x16 opening 16x16 Korean proof."""

from __future__ import annotations

from pathlib import Path

from build_opening_dialogue_16x16_proof import (
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    ENTRY_HOOK,
    HELPER_CODE,
    MARKER_HOOK,
    ORIGINAL_RECORD,
    PAIR_GLYPH_CODES,
    PAIR_SOURCE_CODES,
    PROOF_RECORD,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
    apply_opening_16x16_proof,
    physical_tile_for_code,
    validate_opening_16x16_catalog,
)


def make_fixture() -> bytes:
    rom = bytearray(16 + 0x20000 + 0x20000)
    rom[:4] = b"NES\x1a"
    rom[4] = 8
    rom[5] = 16
    rom[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = ORIGINAL_RECORD
    rom[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] = RENDER_ENTRY_ORIGINAL
    rom[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] = RENDER_MARKER_ORIGINAL
    rom[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] = b"\xff" * CODE_CAVE_SIZE
    return bytes(rom)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalog = validate_opening_16x16_catalog(
        root / "text_data" / "korean_scene_batches" / "opening_ptr_182_16x16.json"
    )
    assert catalog["encoded"] == PROOF_RECORD
    assert len(PROOF_RECORD) == RECORD_LENGTH
    assert len(PAIR_SOURCE_CODES) == len(set(PAIR_SOURCE_CODES)) == 16

    glyphs = {
        glyph: tuple(bytes([index + part]) * 16 for part in range(1, 5))
        for index, glyph in enumerate(PAIR_GLYPH_CODES)
    }
    patched, targets = apply_opening_16x16_proof(make_fixture(), glyphs)
    assert patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] == PROOF_RECORD
    assert patched[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + 3] == ENTRY_HOOK
    assert patched[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + 3] == MARKER_HOOK
    assert patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + len(HELPER_CODE)] == HELPER_CODE
    font_targets = [target for target in targets if str(target["kind"]).startswith("font_tile_")]
    assert len(font_targets) == len(PAIR_GLYPH_CODES) * 4
    assert {int(str(target["code"]), 16) for target in font_targets} == {
        code for code in PAIR_SOURCE_CODES
    } | {code + 0x20 for code in PAIR_SOURCE_CODES}
    assert all(
        int(str(target["physical_tile"]), 16) == physical_tile_for_code(int(str(target["code"]), 16))
        for target in font_targets
    )
    print("Opening dialogue 16x16 paired-cell proof tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

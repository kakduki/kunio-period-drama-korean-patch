#!/usr/bin/env python3
"""Focused tests for the bounded opening-dialogue 8x16 proof patch."""

from __future__ import annotations

from build_opening_dialogue_8x16_proof import (
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    ENTRY_HOOK,
    HELPER_CODE,
    KOREAN_GLYPH_CODES,
    MARKER_HOOK,
    ORIGINAL_RECORD,
    PROOF_RECORD,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_ENTRY_ORIGINAL,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
    apply_opening_8x16_proof,
    physical_tile_for_code,
    validate_opening_catalog,
)
from compile_korean_scene_batch import DEFAULT_CATALOG


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
    catalog = validate_opening_catalog(DEFAULT_CATALOG)
    assert catalog["records"][0]["encoded"] == PROOF_RECORD
    base = make_fixture()
    glyphs = {
        code: (bytes([code]) * 16, bytes([code + 0x20]) * 16)
        for code in KOREAN_GLYPH_CODES.values()
    }
    patched, targets = apply_opening_8x16_proof(base, glyphs)

    assert patched[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + 3] == ENTRY_HOOK
    assert patched[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + 3] == MARKER_HOOK
    assert patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + len(HELPER_CODE)] == HELPER_CODE
    top = [target for target in targets if target["kind"] == "font_tile_top"]
    bottom = [target for target in targets if target["kind"] == "font_tile_bottom"]
    assert len(top) == len(KOREAN_GLYPH_CODES)
    assert len(bottom) == len(KOREAN_GLYPH_CODES)
    assert all(int(str(target["physical_tile"]), 16) == physical_tile_for_code(int(str(target["code"]), 16)) for target in top + bottom)
    assert len(HELPER_CODE) <= CODE_CAVE_SIZE
    print("Opening dialogue 8x16 proof patch tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Focused tests for the bounded opening-dialogue proof patch."""

from __future__ import annotations

from build_opening_dialogue_proof import (
    CHR_BANK,
    KOREAN_GLYPH_CODES,
    ORIGINAL_RECORD,
    POINTER_ROM_OFFSET,
    PROOF_RECORD,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    apply_opening_proof,
    physical_tile_for_code,
)


def make_fixture() -> bytes:
    rom = bytearray(16 + 0x20000 + 0x20000)
    rom[:4] = b"NES\x1a"
    rom[4] = 8
    rom[5] = 16
    rom[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = ORIGINAL_RECORD
    return bytes(rom)


def main() -> int:
    base = make_fixture()
    glyphs = {code: bytes([code]) * 16 for code in KOREAN_GLYPH_CODES.values()}
    patched, targets = apply_opening_proof(base, glyphs)

    assert len(PROOF_RECORD) == RECORD_LENGTH
    assert PROOF_RECORD[-1] == 0xFF
    assert patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] == PROOF_RECORD
    assert patched[POINTER_ROM_OFFSET:POINTER_ROM_OFFSET + 2] == base[POINTER_ROM_OFFSET:POINTER_ROM_OFFSET + 2]
    font_targets = [target for target in targets if target["kind"] == "font_tile"]
    assert len(font_targets) == len(KOREAN_GLYPH_CODES)
    assert all(target["physical_tile"].startswith("0x1") for target in font_targets)
    assert all(target["physical_tile"] not in {"0x18A", "0x18B"} for target in font_targets)
    assert physical_tile_for_code(0x81) == 0x181
    assert CHR_BANK == 7
    print("Opening dialogue proof patch tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

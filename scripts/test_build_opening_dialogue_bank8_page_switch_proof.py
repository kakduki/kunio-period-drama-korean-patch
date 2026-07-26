#!/usr/bin/env python3
"""Test the bounded Bank 8 clone-page candidate against the base ROM."""

from __future__ import annotations

import hashlib

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_bank8_page_switch_proof import (
    PAGE_CHR_BANK,
    PAGE_GLYPH_CODE_PAIRS,
    PAGE_SWITCH_RECORD,
    SOURCE_CHR_BANK,
    apply_page_switch_candidate,
    page_switch_helper,
    page_tile_offset,
)
from build_opening_dialogue_16x16_proof import build_square_glyph_tiles, default_square_font
from build_opening_dialogue_8x16_proof import (
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ROM_OFFSET,
)
from build_opening_dialogue_proof import BASE_MD5, ORIGINAL_RECORD, RECORD_LENGTH, resolve_base_rom


def main() -> int:
    base = resolve_base_rom(None).read_bytes()
    assert hashlib.md5(base).hexdigest() == BASE_MD5
    glyph_tiles = build_square_glyph_tiles(default_square_font(None), PAGE_GLYPH_CODE_PAIRS)
    patched, targets = apply_page_switch_candidate(base, glyph_tiles)
    layout = parse_ines_layout(base)

    assert patched != base
    assert patched[RENDER_ENTRY_ROM_OFFSET : RENDER_ENTRY_ROM_OFFSET + 3] != base[
        RENDER_ENTRY_ROM_OFFSET : RENDER_ENTRY_ROM_OFFSET + 3
    ]
    assert patched[CODE_CAVE_ROM_OFFSET : CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] != b"\xff" * CODE_CAVE_SIZE
    helper, _ = page_switch_helper()
    assert b"\xA9\x40\x8D\x02\x05\xA9\x42\x8D\x03\x05" in helper
    assert len(PAGE_SWITCH_RECORD) == RECORD_LENGTH
    assert PAGE_SWITCH_RECORD != ORIGINAL_RECORD

    source_start = layout.chr_start + SOURCE_CHR_BANK * 0x2000
    page_start = layout.chr_start + PAGE_CHR_BANK * 0x2000
    assert patched[page_start : page_start + 0x2000] != base[page_start : page_start + 0x2000]
    for glyph, pair in PAGE_GLYPH_CODE_PAIRS.items():
        for code in (*pair, pair[0] + 0x20, pair[1] + 0x20):
            offset = page_tile_offset(layout, code)
            assert patched[offset : offset + 16] != base[offset : offset + 16], (
                glyph,
                hex(code),
            )
    declared = [
        (int(target["rom_offset"]), int(target["rom_offset"]) + int(target["length"]))
        for target in targets
    ]
    changed = [
        index
        for index, (old, new) in enumerate(zip(base, patched))
        if old != new
    ]
    assert all(any(start <= index < end for start, end in declared) for index in changed)
    print("Opening Bank 8 page-switch proof tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

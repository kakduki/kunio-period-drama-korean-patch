#!/usr/bin/env python3
"""Focused invariants for the scoped 16x16 Korean main-menu candidate."""

from __future__ import annotations

import hashlib

from analyze_reference_ips import parse_ines_layout
from build_main_menu_korean_candidate import (
    BASE_MD5,
    CHR_PAIR_SIZE,
    CLONE_CHR_1K_PAIR,
    FONT_PROFILE,
    GLYPH_CODE_PAIRS,
    MENU_SLOTS,
    RASTER_R1_VALUE_CLONE,
    RASTER_R1_VALUE_ORIGINAL,
    RASTER_R1_VALUE_ROM_OFFSET,
    SOURCE_CHR_1K_PAIR,
    TEMPLATE_LENGTH,
    TEMPLATE_ROM_OFFSET,
    apply_main_menu_candidate,
    build_menu_template,
    chr_page_offset,
    default_square_font,
    build_square_glyph_tiles,
    resolve_base_rom,
)


def main() -> int:
    base = resolve_base_rom(None).read_bytes()
    assert hashlib.md5(base).hexdigest() == BASE_MD5
    glyph_tiles = build_square_glyph_tiles(
        default_square_font(None),
        GLYPH_CODE_PAIRS,
        font_profile=FONT_PROFILE,
    )
    patched, targets = apply_main_menu_candidate(base, glyph_tiles)
    layout = parse_ines_layout(base)
    source_start = chr_page_offset(layout, SOURCE_CHR_1K_PAIR)
    clone_start = chr_page_offset(layout, CLONE_CHR_1K_PAIR)

    assert patched != base
    assert base[RASTER_R1_VALUE_ROM_OFFSET] == RASTER_R1_VALUE_ORIGINAL
    assert patched[RASTER_R1_VALUE_ROM_OFFSET] == RASTER_R1_VALUE_CLONE
    assert patched[source_start : source_start + CHR_PAIR_SIZE] == base[
        source_start : source_start + CHR_PAIR_SIZE
    ]
    assert patched[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH] == build_menu_template(base)

    template = build_menu_template(base)
    for index, (label_id, _legacy_row, column, _width) in enumerate(MENU_SLOTS):
        top_row = 24 if index < 4 else 26
        top_offset = (top_row - 24) * 32 + column
        assert all(0x80 <= code < 0xA0 for code in template[top_offset : top_offset + 4])

    target_ranges = [
        (int(target["rom_offset"]), int(target["rom_offset"]) + int(target["length"]))
        for target in targets
    ]
    changed = [index for index, (old, new) in enumerate(zip(base, patched)) if old != new]
    assert changed
    assert all(any(start <= offset < end for start, end in target_ranges) for offset in changed)
    assert patched[clone_start : clone_start + CHR_PAIR_SIZE] != base[
        clone_start : clone_start + CHR_PAIR_SIZE
    ]
    print("Main-menu Korean candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

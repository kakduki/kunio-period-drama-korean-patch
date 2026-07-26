#!/usr/bin/env python3
"""Focused dependency-free tests for NES Korean-tile serialization."""

from __future__ import annotations

from korean_tile_font import (
    bitmap_to_nes_2bpp,
    handcrafted_glyph_to_bitmap,
    render_tile,
    square_bitmap_to_nes_2bpp_tiles,
    tall_bitmap_to_nes_2bpp_tiles,
)


def main() -> int:
    bitmap = [[0] * 8 for _ in range(8)]
    bitmap[0][0] = 1
    bitmap[7][7] = 1
    tile = bitmap_to_nes_2bpp(bitmap)
    assert len(tile) == 16
    assert tile[:8] == bytes([0x80, 0, 0, 0, 0, 0, 0, 0x01])
    assert tile[8:] == tile[:8]

    kuk = handcrafted_glyph_to_bitmap("\uCFE0")
    assert len(kuk) == 8 and all(len(row) == 8 for row in kuk)
    assert kuk[0] == [0, 1, 1, 1, 1, 1, 0, 0]
    handcrafted_tile = render_tile("\uCFE0", style="handcrafted")
    assert handcrafted_tile[:8] == bytes([0x7C, 0x40, 0x7C, 0x40, 0x10, 0x10, 0x7C, 0x00])
    assert handcrafted_tile[8:] == handcrafted_tile[:8]
    tall = [[0] * 8 for _ in range(16)]
    tall[0][0] = 1
    tall[8][7] = 1
    top, bottom = tall_bitmap_to_nes_2bpp_tiles(tall)
    assert top[:8] == bytes([0x80, 0, 0, 0, 0, 0, 0, 0])
    assert bottom[:8] == bytes([0x01, 0, 0, 0, 0, 0, 0, 0])
    assert top[8:] == top[:8] and bottom[8:] == bottom[:8]
    square = [[0] * 16 for _ in range(16)]
    square[0][0] = 1
    square[0][8] = 1
    square[8][0] = 1
    square[8][8] = 1
    top_left, top_right, bottom_left, bottom_right = square_bitmap_to_nes_2bpp_tiles(square)
    assert top_left[:8] == bytes([0x80, 0, 0, 0, 0, 0, 0, 0])
    assert top_right[:8] == top_left[:8]
    assert bottom_left[:8] == top_left[:8]
    assert bottom_right[:8] == top_left[:8]
    try:
        handcrafted_glyph_to_bitmap("A")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported handcrafted glyph should fail explicitly")
    print("Korean tile font serialization tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

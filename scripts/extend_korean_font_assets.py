#!/usr/bin/env python3
"""Append a small, repeatable glyph batch to the checked-in 8x16 font assets.

The project font stores one 8x16 monochrome glyph as 16 plane-0 rows followed
by 16 zero plane-1 rows.  Keeping this operation explicit prevents a one-off
candidate builder from silently inventing a different glyph index layout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from korean_tile_font import find_korean_font, normalize_glyph_to_tall_bitmap
from rom_utils import REPO_ROOT


DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
DEFAULT_GLYPHS = "오 건 없 음"


def bitmap_to_font_bytes(bitmap: list[list[int]]) -> bytes:
    if len(bitmap) != 16 or any(len(row) != 8 for row in bitmap):
        raise ValueError("expected an 8x16 bitmap")
    plane0 = bytearray()
    for row in bitmap:
        value = 0
        for column, pixel in enumerate(row):
            if pixel not in (0, 1):
                raise ValueError("bitmap pixels must be 0 or 1")
            value |= pixel << (7 - column)
        plane0.append(value)
    return bytes(plane0 + bytes(16))


def extend(
    char_map_path: Path,
    font_bin_path: Path,
    characters: list[str],
    font_path: Path | None = None,
) -> dict[str, object]:
    payload = json.loads(char_map_path.read_text(encoding="utf-8"))
    current = [str(character) for character in payload["sorted"]]
    font_data = bytearray(font_bin_path.read_bytes())
    expected = len(current) * 32
    if len(font_data) != expected:
        raise ValueError(f"font/map mismatch: {len(font_data)} bytes != {expected}")

    requested = list(dict.fromkeys(characters))
    missing = [character for character in requested if character not in current]
    selected_font = find_korean_font(font_path)
    appended: list[dict[str, object]] = []
    for character in missing:
        glyph = bitmap_to_font_bytes(
            normalize_glyph_to_tall_bitmap(character, font_path=selected_font)
        )
        index = len(current)
        current.append(character)
        font_data.extend(glyph)
        appended.append(
            {
                "character": character,
                "index": index,
                "bytes": glyph.hex(" ").upper(),
            }
        )

    payload["sorted"] = current
    payload["count"] = len(current)
    char_map_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    font_bin_path.write_bytes(font_data)
    return {
        "font": str(font_bin_path),
        "char_map": str(char_map_path),
        "font_path": str(selected_font),
        "requested": requested,
        "appended": appended,
        "count": len(current),
        "font_bytes": len(font_data),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("characters", nargs="*", default=DEFAULT_GLYPHS.split())
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--font-bin", type=Path, default=DEFAULT_FONT_BIN)
    parser.add_argument("--font", type=Path)
    args = parser.parse_args()
    result = extend(
        args.char_map.resolve(),
        args.font_bin.resolve(),
        args.characters,
        args.font.resolve() if args.font else None,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

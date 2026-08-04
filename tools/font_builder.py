#!/usr/bin/env python3
"""Build a compact NES 2bpp tile payload from the project font renderer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import korean_tile_font as font  # noqa: E402


def parse_characters(args: argparse.Namespace) -> str:
    if args.characters_file:
        return args.characters_file.read_text(encoding="utf-8").rstrip("\r\n")
    if args.codepoints:
        values = [item.strip().removeprefix("U+") for item in args.codepoints.split(",") if item.strip()]
        return "".join(chr(int(item, 16)) for item in values)
    if args.characters:
        return args.characters
    raise SystemExit("provide --characters, --characters-file, or --codepoints")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--characters")
    parser.add_argument("--characters-file", type=Path)
    parser.add_argument("--codepoints", help="comma-separated Unicode code points, for example CFE0,B2C8")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font")
    parser.add_argument("--target-pixels", type=int, default=7)
    parser.add_argument("--threshold", type=int, default=92)
    parser.add_argument("--style", choices=("raster", "handcrafted"), default="handcrafted")
    args = parser.parse_args()
    characters = parse_characters(args)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = bytearray()
    for character in characters:
        options = {}
        if args.style == "raster":
            options = {
                "font_path": args.font,
                "target_pixels": args.target_pixels,
                "threshold": args.threshold,
            }
        payload.extend(font.render_tile(character, style=args.style, **options))
    output.write_bytes(payload)
    print(f"font payload={output} characters={len(characters)} bytes={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

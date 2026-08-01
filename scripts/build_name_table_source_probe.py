#!/usr/bin/env python3
"""Build one bounded source-owner probe for the visible name-table sequence."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from build_patch import make_records, write_ips
from korean_tile_font import find_korean_font, render_tile
from rom_utils import REPO_ROOT


EXPECTED = bytes.fromhex("88 96 9F 8B")
TEST_CODES = bytes((0x81, 0x82, 0x81, 0x82))
GLYPHS = ("다", "리", "다", "리")
CHR_SLOT_START = 0x2F820
DEFAULT_INPUT = REPO_ROOT / "output" / "full_nonpointer_korean_candidate" / "kunio_period_drama_korean_full_nonpointer_candidate.nes"


def build(input_rom: Path, offset: int, out_dir: Path, font_arg: str | None) -> tuple[Path, Path]:
    original = input_rom.read_bytes()
    if original[offset:offset + len(EXPECTED)] != EXPECTED:
        raise ValueError(f"offset 0x{offset:05X} does not contain {EXPECTED.hex(' ').upper()}")
    patched = bytearray(original)
    patched[offset:offset + len(TEST_CODES)] = TEST_CODES
    font = find_korean_font(font_arg)
    for index, glyph in enumerate(GLYPHS):
        start = CHR_SLOT_START + index * 0x10
        patched[start:start + 0x10] = render_tile(glyph, font_path=font, target_pixels=7, threshold=92)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"probe_{offset:05X}"
    rom_path = out_dir / f"{stem}.nes"
    ips_path = out_dir / f"{stem}.ips"
    rom_path.write_bytes(patched)
    write_ips(ips_path, make_records(original, bytes(patched)))
    return rom_path, ips_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-rom", default=str(DEFAULT_INPUT))
    parser.add_argument("--offset", required=True, type=lambda value: int(value, 0))
    parser.add_argument("--out-dir", default=r"C:\tmp\kunio_name_source_probes")
    parser.add_argument("--font")
    args = parser.parse_args()
    rom_path, ips_path = build(
        Path(args.input_rom).expanduser().resolve(),
        args.offset,
        Path(args.out_dir).expanduser().resolve(),
        args.font,
    )
    print(f"rom={rom_path}")
    print(f"ips={ips_path}")
    print(f"md5={hashlib.md5(rom_path.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build an experimental Korean font IPS/ROM patch.

The verified CHR Bank 07 map uses 8x8 tile slots at 16 bytes each. Earlier
versions treated those slots as 8x16 indexes and wrote to Bank 08+, so this
builder keeps every generated font byte inside the Bank 07 range.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from rom_utils import REPO_ROOT, find_rom_path


INES_HEADER_SIZE = 0x10
PRG_ROM_SIZE = 0x20000
CHR_BANK_SIZE = 0x2000
CHR_TILE_SIZE = 0x10
CHR_BANK = 7
CHR_START = INES_HEADER_SIZE + PRG_ROM_SIZE
CHR_BANK7_START = CHR_START + CHR_BANK * CHR_BANK_SIZE
CHR_BANK7_END = CHR_BANK7_START + CHR_BANK_SIZE
TARGET_TILE_START = 0x101
TARGET_TILE_END = 0x1B5

DEFAULT_FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_OUT_DIR = REPO_ROOT / "output"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def glyph_8x16_to_8x8_tile(glyph: bytes) -> bytes:
    """Collapse the generated 8x16 2bpp glyph into one 8x8 CHR tile.

    The source generator stores 16 plane-0 rows followed by 16 plane-1 rows.
    Bank7 text slots are currently identified as one 8x8 background tile each,
    so we OR adjacent vertical rows to preserve the whole glyph silhouette.
    """
    if len(glyph) != 32:
        raise ValueError(f"Expected 32-byte 8x16 glyph, got {len(glyph)} bytes")

    plane0 = bytearray(8)
    plane1 = bytearray(8)
    for row in range(8):
        plane0[row] = glyph[row * 2] | glyph[row * 2 + 1]
        plane1[row] = glyph[16 + row * 2] | glyph[16 + row * 2 + 1]
    return bytes(plane0 + plane1)


def make_records(original: bytes, patched: bytes) -> list[tuple[int, bytes]]:
    records: list[tuple[int, bytes]] = []
    idx = 0
    while idx < len(patched):
        if patched[idx] == original[idx]:
            idx += 1
            continue
        start = idx
        data = bytearray()
        while idx < len(patched) and patched[idx] != original[idx]:
            data.append(patched[idx])
            idx += 1
        records.append((start, bytes(data)))
    return records


def write_ips(path: Path, records: list[tuple[int, bytes]]) -> None:
    with path.open("wb") as handle:
        handle.write(b"PATCH")
        for offset, data in records:
            for chunk_start in range(0, len(data), 0xFFFF):
                chunk = data[chunk_start:chunk_start + 0xFFFF]
                handle.write(struct.pack(">I", offset + chunk_start)[1:])
                handle.write(struct.pack(">H", len(chunk)))
                handle.write(chunk)
        handle.write(b"EOF")


def load_characters(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["sorted"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Optional .nes path; defaults to rom/*.nes")
    parser.add_argument("--font-bin", default=str(DEFAULT_FONT_BIN))
    parser.add_argument("--char-map", default=str(DEFAULT_CHAR_MAP))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    if args.rom:
        rom_path = Path(args.rom).expanduser().resolve()
        if not rom_path.exists():
            raise FileNotFoundError(f"ROM not found: {rom_path}")
    else:
        rom_path = find_rom_path()

    font_path = Path(args.font_bin).expanduser().resolve()
    char_map_path = Path(args.char_map).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    original = rom_path.read_bytes()
    patched = bytearray(original)
    font_data = font_path.read_bytes()
    characters = load_characters(char_map_path)

    print(f"ROM: {rom_path}")
    print(f"CHR Bank 07 ROM range: 0x{CHR_BANK7_START:05X}-0x{CHR_BANK7_END - 1:05X}")
    print(f"Target 8x8 tiles: 0x{TARGET_TILE_START:03X}-0x{TARGET_TILE_END:03X}")

    available_slots = TARGET_TILE_END - TARGET_TILE_START + 1
    glyph_count = min(len(font_data) // 32, len(characters), available_slots)
    font_changes = 0
    changed_offsets: list[int] = []

    for index in range(glyph_count):
        source = font_data[index * 32:index * 32 + 32]
        target_tile = TARGET_TILE_START + index
        target_offset = CHR_BANK7_START + target_tile * CHR_TILE_SIZE
        target_end = target_offset + CHR_TILE_SIZE
        if not CHR_BANK7_START <= target_offset < target_end <= CHR_BANK7_END:
            raise RuntimeError(f"Tile 0x{target_tile:03X} escaped CHR Bank 07")

        tile = glyph_8x16_to_8x8_tile(source)
        if bytes(patched[target_offset:target_end]) != tile:
            patched[target_offset:target_end] = tile
            font_changes += 1
            changed_offsets.extend(range(target_offset, target_end))

    escaped = [
        offset for offset in changed_offsets
        if not CHR_BANK7_START <= offset < CHR_BANK7_END
    ]
    if escaped:
        raise RuntimeError(f"{len(escaped)} changed byte(s) escaped CHR Bank 07")

    records = make_records(original, bytes(patched))
    ips_path = out_dir / "kunio_period_drama_korean_v0.1.ips"
    patched_path = out_dir / "kunio_period_drama_korean_v0.1.nes"
    report_path = out_dir / "kunio_period_drama_korean_v0.1_build_report.json"

    write_ips(ips_path, records)
    patched_path.write_bytes(patched)

    report = {
        "rom": str(rom_path),
        "original_md5": md5(original),
        "patched_md5": md5(bytes(patched)),
        "chr_bank7_range": [f"0x{CHR_BANK7_START:05X}", f"0x{CHR_BANK7_END - 1:05X}"],
        "target_tile_range": [f"0x{TARGET_TILE_START:03X}", f"0x{TARGET_TILE_END:03X}"],
        "glyphs_written": glyph_count,
        "font_tiles_changed": font_changes,
        "changed_bytes": len(changed_offsets),
        "escaped_chr_bank7_bytes": len(escaped),
        "ips_records": len(records),
        "ips_path": str(ips_path),
        "patched_rom_path": str(patched_path),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\nIPS patch generated")
    print(f"  IPS: {ips_path} ({ips_path.stat().st_size} bytes)")
    print(f"  patched ROM: {patched_path}")
    print(f"  report: {report_path}")
    print(f"  glyphs written: {glyph_count}")
    print(f"  changed bytes in CHR Bank7: {len(changed_offsets)}")
    print(f"  IPS records: {len(records)}")
    print(f"  original MD5: {report['original_md5']}")
    print(f"  patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

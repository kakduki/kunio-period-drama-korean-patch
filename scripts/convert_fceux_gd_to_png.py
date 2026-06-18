#!/usr/bin/env python3
"""Convert FCEUX gd truecolor screenshots to PNG files."""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def parse_gd_truecolor(data: bytes) -> tuple[int, int, bytes]:
    if len(data) < 11:
        raise ValueError("GD file is too small for a truecolor header")
    if data[:2] != b"\xff\xfe":
        raise ValueError("unsupported GD signature; expected truecolor FF FE")

    width = int.from_bytes(data[2:4], "big")
    height = int.from_bytes(data[4:6], "big")
    truecolor = data[6]
    if truecolor != 1:
        raise ValueError(f"unsupported GD color mode {truecolor}; expected truecolor mode 1")

    pixel_data = data[11:]
    expected_len = width * height * 4
    if len(pixel_data) != expected_len:
        raise ValueError(f"pixel data length mismatch: expected {expected_len}, got {len(pixel_data)}")
    return width, height, pixel_data


def gd_pixels_to_png_rgb(width: int, height: int, pixel_data: bytes) -> bytes:
    rows = bytearray()
    stride = width * 4
    for y in range(height):
        rows.append(0)
        base = y * stride
        for x in range(width):
            p = base + x * 4
            rows.extend(pixel_data[p + 1 : p + 4])

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + _png_chunk(b"IEND", b"")
    )


def convert_file(source: Path, destination: Path) -> None:
    width, height, pixels = parse_gd_truecolor(source.read_bytes())
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(gd_pixels_to_png_rgb(width, height, pixels))


def convert_path(source: Path, destination: Path | None) -> list[Path]:
    if source.is_dir():
        output_dir = destination or source
        written = []
        for gd_file in sorted(source.glob("*.gd")):
            png_file = output_dir / (gd_file.stem + ".png")
            convert_file(gd_file, png_file)
            written.append(png_file)
        return written

    png_file = destination or source.with_suffix(".png")
    convert_file(source, png_file)
    return [png_file]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Input .gd file or directory")
    parser.add_argument("destination", type=Path, nargs="?", help="Output .png file or directory")
    args = parser.parse_args()

    written = convert_path(args.source, args.destination)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

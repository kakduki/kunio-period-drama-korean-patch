#!/usr/bin/env python3
"""Extract CHR ROM tiles as preview images."""
from PIL import Image

from rom_utils import analysis_dir, find_rom_path


ROM_PATH = find_rom_path()
OUT_DIR = analysis_dir("font")

with open(ROM_PATH, "rb") as f:
    data = f.read()

chr_rom = data[16 + 131072:]  # CHR ROM: 131072 bytes
colors = [(255, 255, 255), (200, 200, 200), (120, 120, 120), (0, 0, 0)]

print("=" * 60)
print("CHR ROM font analysis and 8x16 font preparation")
print("=" * 60)

for bank in range(16):
    bank_data = chr_rom[bank * 8192:(bank + 1) * 8192]

    img_8x16 = Image.new("RGB", (8 * 16, 16 * 16), (255, 255, 255))
    px = img_8x16.load()

    for char_idx in range(256):
        base = char_idx * 32
        if base + 32 > len(bank_data):
            break

        cx = (char_idx % 16) * 8
        cy = (char_idx // 16) * 16

        for row in range(16):
            byte_plane0 = bank_data[base + row]
            byte_plane1 = bank_data[base + row + 16]

            for col in range(8):
                bit0 = (byte_plane0 >> (7 - col)) & 1
                bit1 = (byte_plane1 >> (7 - col)) & 1
                pixel = bit0 | (bit1 << 1)
                px[cx + col, cy + row] = colors[pixel]

    img_8x16.save(OUT_DIR / f"chr_bank_{bank:02d}_8x16.png")

    img_8x8 = Image.new("RGB", (8 * 32, 8 * 16), (255, 255, 255))
    px8 = img_8x8.load()

    for tile_idx in range(512):
        base = tile_idx * 16
        if base + 16 > len(bank_data):
            break

        tx = (tile_idx % 32) * 8
        ty = (tile_idx // 32) * 8

        for row in range(8):
            byte_p0 = bank_data[base + row]
            byte_p1 = bank_data[base + 8 + row]

            for col in range(8):
                bit0 = (byte_p0 >> (7 - col)) & 1
                bit1 = (byte_p1 >> (7 - col)) & 1
                pixel = bit0 | (bit1 << 1)
                px8[tx + col, ty + row] = colors[pixel]

    img_8x8.save(OUT_DIR / f"chr_bank_{bank:02d}_8x8.png")

print("CHR bank images generated.")

print("\n=== 8x16 tile usage by bank ===")
for bank in range(16):
    bank_data = chr_rom[bank * 8192:(bank + 1) * 8192]
    used_tiles = 0
    for char_idx in range(256):
        base = char_idx * 32
        total = sum(bank_data[base:base + 32])
        if total > 0 and total < 255 * 32:
            used_tiles += 1
    print(f"  Bank {bank:02d}: {used_tiles}/256 tiles used")

#!/usr/bin/env python3
"""Render a labeled CHR bank sheet for local visual analysis."""
import sys

from PIL import Image, ImageDraw, ImageFont

from rom_utils import analysis_dir, find_rom_path


bank = int(sys.argv[1], 0) if len(sys.argv) > 1 else 7
mode = sys.argv[2] if len(sys.argv) > 2 else "8x16"
scale = int(sys.argv[3], 0) if len(sys.argv) > 3 else 4
sys.argv = sys.argv[:1]
label_h = 10
tile_w = 8 * scale
tile_h = (8 if mode == "8x8" else 16) * scale
cell_w = tile_w
cell_h = tile_h + label_h
colors = [(255, 255, 255), (190, 190, 190), (90, 90, 90), (0, 0, 0)]

with open(find_rom_path(), "rb") as f:
    data = f.read()

chr_rom = data[16 + 131072:]
bank_data = chr_rom[bank * 8192:(bank + 1) * 8192]
out_dir = analysis_dir("font")

tile_count = 512 if mode == "8x8" else 256
rows = 16 if mode == "8x16" else 16
cols = 16 if mode == "8x16" else 32
sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (240, 240, 240))
draw = ImageDraw.Draw(sheet)
font = ImageFont.load_default()

for char_idx in range(tile_count):
    base = char_idx * (16 if mode == "8x8" else 32)
    if base + (16 if mode == "8x8" else 32) > len(bank_data):
        break

    cx = (char_idx % cols) * cell_w
    cy = (char_idx // cols) * cell_h
    draw.text((cx + 1, cy), f"{char_idx:03X}" if mode == "8x8" else f"{char_idx:02X}", fill=(180, 0, 0), font=font)

    for row in range(8 if mode == "8x8" else 16):
        byte_plane0 = bank_data[base + row]
        byte_plane1 = bank_data[base + row + (8 if mode == "8x8" else 16)]
        for col in range(8):
            bit0 = (byte_plane0 >> (7 - col)) & 1
            bit1 = (byte_plane1 >> (7 - col)) & 1
            pixel = bit0 | (bit1 << 1)
            x0 = cx + col * scale
            y0 = cy + label_h + row * scale
            draw.rectangle(
                [x0, y0, x0 + scale - 1, y0 + scale - 1],
                fill=colors[pixel],
            )

out_path = out_dir / f"chr_bank_{bank:02d}_{mode}_labeled.png"
sheet.save(out_path)
print(out_path)

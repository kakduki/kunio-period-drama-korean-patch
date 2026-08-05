from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_patch import glyph_8x16_to_8x8_tile

one_bpp = bytes([0x3C, 0x42, 0x81, 0x81, 0x42, 0x3C, 0, 0] + [0] * 24)
tile = glyph_8x16_to_8x8_tile(one_bpp)
assert tile[:8] == tile[8:], tile.hex()
true_2bpp = bytes([0xFF] * 16 + [0xAA] * 16)
tile2 = glyph_8x16_to_8x8_tile(true_2bpp)
assert tile2[:8] == bytes([0xFF] * 8)
assert tile2[8:] == bytes([0xAA] * 8)
print("glyph palette promotion checks passed")
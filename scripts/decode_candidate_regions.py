#!/usr/bin/env python3
"""Decode candidate PRG regions with tentative kana offsets."""
from rom_utils import find_rom_path


KANA_BY_LOW = {
    0x01: "\u3042", 0x02: "\u3044", 0x03: "\u3046", 0x04: "\u3048", 0x05: "\u304a",
    0x06: "\u304b", 0x07: "\u304d", 0x08: "\u304f", 0x09: "\u3051", 0x0A: "\u3053",
    0x0B: "\u3055", 0x0C: "\u3057", 0x0D: "\u3059", 0x0E: "\u305b", 0x0F: "\u305d",
    0x10: "\u305f", 0x11: "\u3061", 0x12: "\u3064", 0x13: "\u3066", 0x14: "\u3068",
    0x15: "\u306a", 0x16: "\u306b", 0x17: "\u306c", 0x18: "\u306d", 0x19: "\u306e",
    0x1A: "\u306f", 0x1B: "\u3072", 0x1C: "\u3075", 0x1D: "\u3078", 0x1E: "\u307b",
    0x20: "\u307e", 0x21: "\u307f", 0x22: "\u3080", 0x23: "\u3081", 0x24: "\u3082",
    0x25: "\u3084", 0x26: "\u3086", 0x27: "\u3088",
    0x28: "\u3089", 0x29: "\u308a", 0x2A: "\u308b", 0x2B: "\u308c", 0x2C: "\u308d",
    0x2D: "\u308f", 0x2E: "\u3092", 0x2F: "\u3093",
}

WATCH_REGIONS = [
    ("bank1_items_a", 0x05600, 0x05800, [0x7A, 0x7C, 0x82]),
    ("bank1_items_b", 0x06240, 0x063A0, [0x7C, 0x82, 0x84]),
    ("bank1_status_a", 0x065C0, 0x06C00, [0x7C, 0x80, 0x82]),
    ("bank1_status_b", 0x07140, 0x07400, [0x82, 0x84, 0x93]),
    ("bank5_cluster", 0x17D00, 0x17DA0, [0x75, 0x76]),
]


def decode_byte(byte: int, add: int) -> str:
    low = (byte - add) & 0xFF
    if low in KANA_BY_LOW:
        return KANA_BY_LOW[low]
    if byte == 0x00:
        return "\u00b7"
    if byte == 0xFF:
        return "|"
    if byte in (0xF0, 0xF8, 0xF9):
        return "\u25a1"
    if 0x20 <= byte <= 0x7E:
        return chr(byte)
    return "."


def score_window(data: bytes, add: int) -> int:
    kana = sum(1 for b in data if ((b - add) & 0xFF) in KANA_BY_LOW)
    delimiters = sum(1 for b in data if b in (0x00, 0xFF, 0xF0, 0xF8, 0xF9))
    return kana * 2 + delimiters


def hex_line(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)


with open(find_rom_path(), "rb") as f:
    rom = f.read()

prg = rom[16:16 + 131072]

print("=== Candidate region offset decoding ===")
print("Legend: middot=00, |=FF, square=F0/F8/F9, dots=unknown/non-kana")
print()

for name, start, end, offsets in WATCH_REGIONS:
    print(f"## {name} PRG+0x{start:05X}-0x{end:05X} ROM+0x{start + 16:05X}-0x{end + 16:05X}")
    raw = prg[start:end]
    for add in offsets:
        print(f"\n-- add=0x{add:02X} --")
        scored = []
        for pos in range(0, len(raw), 16):
            chunk = raw[pos:pos + 16]
            scored.append((score_window(chunk, add), start + pos, chunk))
        for score, abs_pos, chunk in sorted(scored, reverse=True)[:12]:
            decoded = "".join(decode_byte(b, add) for b in chunk)
            print(f"PRG+0x{abs_pos:05X} score={score:02d} {hex_line(chunk):47s}  {decoded}")
    print()

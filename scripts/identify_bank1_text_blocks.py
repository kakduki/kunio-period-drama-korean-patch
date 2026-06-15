#!/usr/bin/env python3
"""Identify PRG bank 1 text-like blocks around ROM+0x05610.

This pass follows the current working hypothesis:

    PRG text byte + 0x7A = CHR bank 07 tile index

For hiragana in CHR bank 07, tile indexes are treated as 0x101..0x12F.
The script also reports exact matches against translation_data.txt entries that
can be represented by the current hiragana-only map.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from rom_utils import find_rom_path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_DATA = ROOT / "text_data" / "translation_data.txt"
OUT = ROOT / "rom_analysis" / "bank1_text_block_map.md"

ROM_START = 0x05610
ROM_END = 0x05810
PRG_HEADER = 0x10
CHR_ADD = 0x7A

HIRAGANA_BY_LOW = {
    0x01: "あ", 0x02: "い", 0x03: "う", 0x04: "え", 0x05: "お",
    0x06: "か", 0x07: "き", 0x08: "く", 0x09: "け", 0x0A: "こ",
    0x0B: "さ", 0x0C: "し", 0x0D: "す", 0x0E: "せ", 0x0F: "そ",
    0x10: "た", 0x11: "ち", 0x12: "つ", 0x13: "て", 0x14: "と",
    0x15: "な", 0x16: "に", 0x17: "ぬ", 0x18: "ね", 0x19: "の",
    0x1A: "は", 0x1B: "ひ", 0x1C: "ふ", 0x1D: "へ", 0x1E: "ほ",
    0x20: "ま", 0x21: "み", 0x22: "む", 0x23: "め", 0x24: "も",
    0x25: "や", 0x26: "ゆ", 0x27: "よ",
    0x28: "ら", 0x29: "り", 0x2A: "る", 0x2B: "れ", 0x2C: "ろ",
    0x2D: "わ", 0x2E: "を", 0x2F: "ん",
}
LOW_BY_HIRAGANA = {v: k for k, v in HIRAGANA_BY_LOW.items()}

KATAKANA_TO_HIRAGANA = str.maketrans(
    {chr(code): chr(code - 0x60) for code in range(ord("ァ"), ord("ヶ") + 1)}
)


@dataclass
class Block:
    index: int
    rom_start: int
    rom_end: int
    prg_start: int
    data: bytes
    decoded: str
    kana_count: int
    unknown_count: int


@dataclass
class TranslationEntry:
    source: str
    korean: str
    category: str
    note: str
    normalized: str


def normalize_japanese(text: str) -> str:
    text = text.translate(KATAKANA_TO_HIRAGANA)
    text = re.sub(r"[！!？?・ 　ー\-]", "", text)
    return text


def decode_byte(byte: int) -> str:
    tile = byte + CHR_ADD
    if 0x101 <= tile <= 0x12F:
        return HIRAGANA_BY_LOW.get(tile - 0x100, "?")
    if byte == 0x00:
        return "·"
    if byte == 0xFF:
        return "|"
    if byte in (0xF0, 0xF8, 0xF9):
        return "□"
    if 0x20 <= byte <= 0x7E:
        return f"<{byte:02X}>"
    return "."


def decode_bytes(data: bytes) -> tuple[str, int, int]:
    chars = [decode_byte(byte) for byte in data]
    decoded = "".join(chars)
    kana_count = sum(ch in LOW_BY_HIRAGANA for ch in chars)
    unknown_count = sum(1 for ch in chars if ch in {".", "?"})
    return decoded, kana_count, unknown_count


def encode_hiragana(text: str) -> bytes | None:
    normalized = normalize_japanese(text)
    out = []
    for ch in normalized:
        low = LOW_BY_HIRAGANA.get(ch)
        if low is None:
            return None
        out.append(((0x100 + low) - CHR_ADD) & 0xFF)
    return bytes(out)


def split_blocks(blob: bytes, rom_start: int) -> list[Block]:
    blocks: list[Block] = []
    pos = 0
    index = 1
    while pos < len(blob):
        while pos < len(blob) and blob[pos] == 0xFF:
            pos += 1
        start = pos
        while pos < len(blob) and blob[pos] != 0xFF:
            pos += 1
        data = blob[start:pos]
        if data:
            decoded, kana_count, unknown_count = decode_bytes(data)
            blocks.append(
                Block(
                    index=index,
                    rom_start=rom_start + start,
                    rom_end=rom_start + pos,
                    prg_start=rom_start + start - PRG_HEADER,
                    data=data,
                    decoded=decoded,
                    kana_count=kana_count,
                    unknown_count=unknown_count,
                )
            )
            index += 1
    return blocks


def read_translation_entries() -> list[TranslationEntry]:
    entries: list[TranslationEntry] = []
    for raw in TRANSLATION_DATA.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        while len(parts) < 4:
            parts.append("")
        entries.append(
            TranslationEntry(
                source=parts[0],
                korean=parts[1],
                category=parts[2],
                note=parts[3],
                normalized=normalize_japanese(parts[0]),
            )
        )
    return entries


def find_all(haystack: bytes, needle: bytes) -> list[int]:
    offsets = []
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            break
        offsets.append(idx)
        start = idx + 1
    return offsets


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def main() -> int:
    rom = Path(find_rom_path()).read_bytes()
    blob = rom[ROM_START:ROM_END]
    blocks = split_blocks(blob, ROM_START)
    entries = read_translation_entries()

    exact_matches = []
    for entry in entries:
        encoded = encode_hiragana(entry.source)
        if not encoded or len(encoded) < 2:
            continue
        for rel in find_all(blob, encoded):
            rom_offset = ROM_START + rel
            exact_matches.append((entry, encoded, rom_offset, rom_offset - PRG_HEADER))

    lines: list[str] = []
    lines.append("# PRG bank 1 text block map")
    lines.append("")
    lines.append(f"Range analyzed: `ROM+0x{ROM_START:05X}-0x{ROM_END:05X}` (`PRG+0x{ROM_START - PRG_HEADER:05X}-0x{ROM_END - PRG_HEADER:05X}`)")
    lines.append("")
    lines.append("Decoder hypothesis: `CHR tile = PRG byte + 0x7A`, using CHR bank 07 hiragana tile range `0x101-0x12F`.")
    lines.append("")
    lines.append("## Block table")
    lines.append("")
    lines.append("| # | ROM offset | PRG offset | bytes | kana/unknown | decoded guess |")
    lines.append("| ---: | --- | --- | ---: | --- | --- |")
    for block in blocks:
        lines.append(
            f"| {block.index} | `0x{block.rom_start:05X}-0x{block.rom_end:05X}` | "
            f"`0x{block.prg_start:05X}` | {len(block.data)} | "
            f"{block.kana_count}/{block.unknown_count} | `{block.decoded}` |"
        )

    lines.append("")
    lines.append("## Exact translation-data matches under +0x7A hypothesis")
    lines.append("")
    if not exact_matches:
        lines.append("No exact translation entries matched this range with the current hiragana-only +0x7A encoder.")
    else:
        lines.append("| ROM offset | PRG offset | Japanese | Korean | category | encoded bytes |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for entry, encoded, rom_offset, prg_offset in exact_matches:
            lines.append(
                f"| `0x{rom_offset:05X}` | `0x{prg_offset:05X}` | {entry.source} | "
                f"{entry.korean} | {entry.category} | `{hex_bytes(encoded)}` |"
            )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `0xFF` is used here as a tentative block delimiter because it repeatedly separates readable-looking byte runs in this range.")
    lines.append("- This is a block map, not yet proof that every block is user-visible text. FCEUX read/write tracing still needs to connect these offsets to specific runtime screens.")
    lines.append("- If expected entries such as `カタナ` do not match exactly under `+0x7A`, compare with the older offset-scan results in `candidate_region_decode.txt` and `kana_pattern_scan.txt`; some tables may use a related but shifted encoding.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"blocks={len(blocks)} exact_matches={len(exact_matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

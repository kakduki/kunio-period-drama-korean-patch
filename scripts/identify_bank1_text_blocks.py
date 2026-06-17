#!/usr/bin/env python3
"""Identify PRG bank 1 text-like blocks around ROM+0x05610.

This pass follows the current working hypothesis:

    PRG text byte + 0x7A = CHR bank 07 tile index

For hiragana in CHR bank 07, tile indexes are treated as 0x101..0x12F.
The script also reports exact matches against translation_data.txt entries that
can be represented by the current hiragana-only map.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re

from map_translation_offsets import (
    BANK1_ROM_END,
    BANK1_ROM_START,
    PRG_HEADER,
    WATCH_ROM_END,
    WATCH_ROM_START,
    Hit,
    collect_hits,
    fmt_bytes,
    read_entries,
)
from rom_utils import find_rom_path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_DATA = ROOT / "text_data" / "translation_data.txt"
OUT = ROOT / "rom_analysis" / "bank1_text_block_map.md"

ROM_START = 0x05610
ROM_END = 0x05810
CHR_ADD = 0x7A
SHIFT_BASE_MIN = 0x70
SHIFT_BASE_MAX = 0x9F

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


@dataclass
class DecodeCandidate:
    base: int
    decoded: str
    kana_count: int
    marker_count: int

    @property
    def score(self) -> tuple[int, int, int]:
        return (self.kana_count, -self.marker_count, -abs(self.base - 0x82))


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


def decode_shifted_byte(byte: int, base: int) -> str:
    low = (byte - base) & 0xFF
    return HIRAGANA_BY_LOW.get(low, f"<{byte:02X}>")


def decode_shifted_bytes(data: bytes, base: int) -> DecodeCandidate:
    chars = [decode_shifted_byte(byte, base) for byte in data]
    decoded = "".join(chars)
    kana_count = sum(ch in LOW_BY_HIRAGANA for ch in chars)
    marker_count = decoded.count("<")
    return DecodeCandidate(base, decoded, kana_count, marker_count)


def best_shifted_decodes(data: bytes, limit: int = 3) -> list[DecodeCandidate]:
    candidates = [
        decode_shifted_bytes(data, base)
        for base in range(SHIFT_BASE_MIN, SHIFT_BASE_MAX + 1)
    ]
    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates[:limit]


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


def block_for_offset(blocks: list[Block], rom_offset: int) -> Block | None:
    for block in blocks:
        if block.rom_start <= rom_offset < block.rom_end:
            return block
    return None


def format_hit(hit: Hit) -> str:
    return (
        f"`0x{hit.rom_offset:05X}` {hit.entry.source}->{hit.entry.korean} "
        f"({hit.entry.category}, {hit.mode}/`0x{hit.base:02X}`, `{fmt_bytes(hit.encoded)}`)"
    )


def main() -> int:
    rom = Path(find_rom_path()).read_bytes()
    blob = rom[ROM_START:ROM_END]
    blocks = split_blocks(blob, ROM_START)
    entries = read_translation_entries()
    translation_hits = [
        hit for hit in collect_hits(rom[PRG_HEADER:PRG_HEADER + 0x20000], read_entries())
        if WATCH_ROM_START <= hit.rom_offset < WATCH_ROM_END
    ]
    hits_by_block: dict[int, list[Hit]] = defaultdict(list)
    for hit in translation_hits:
        block = block_for_offset(blocks, hit.rom_offset)
        if block:
            hits_by_block[block.index].append(hit)

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
    lines.append("## Block-level multi-base decode summary")
    lines.append("")
    lines.append(
        "This table keeps the original `+0x7A` decode, then adds the best shifted-low decodes "
        "(`PRG byte = hiragana_low + base`) and any translation-data hits that land inside the block."
    )
    lines.append("")
    lines.append("| # | ROM range | bytes | +0x7A decode | best shifted-low decodes | translation hits in block |")
    lines.append("| ---: | --- | --- | --- | --- | --- |")
    for block in blocks:
        best = best_shifted_decodes(block.data)
        best_text = "<br>".join(
            f"`base 0x{candidate.base:02X}` {candidate.kana_count}/{candidate.marker_count}: `{candidate.decoded}`"
            for candidate in best
        )
        block_hits = hits_by_block.get(block.index, [])
        hit_text = "<br>".join(format_hit(hit) for hit in block_hits) if block_hits else "-"
        lines.append(
            f"| {block.index} | `0x{block.rom_start:05X}-0x{block.rom_end:05X}` | "
            f"`{hex_bytes(block.data)}` | `{block.decoded}` | {best_text} | {hit_text} |"
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
    lines.append("## All translation-data hits inside watch range")
    lines.append("")
    if not translation_hits:
        lines.append("No translation-data candidates landed inside this watch range.")
    else:
        lines.append("| block | ROM offset | PRG offset | mode/base | Japanese | Korean | category | bytes |")
        lines.append("| ---: | --- | --- | --- | --- | --- | --- | --- |")
        for hit in sorted(translation_hits, key=lambda h: (h.rom_offset, h.mode, h.base, h.entry.source)):
            block = block_for_offset(blocks, hit.rom_offset)
            lines.append(
                f"| {block.index if block else '-'} | `0x{hit.rom_offset:05X}` | `0x{hit.prg_offset:05X}` | "
                f"{hit.mode}/`0x{hit.base:02X}` | {hit.entry.source} | {hit.entry.korean} | "
                f"{hit.entry.category} | `{fmt_bytes(hit.encoded)}` |"
            )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `0xFF` is used here as a tentative block delimiter because it repeatedly separates readable-looking byte runs in this range.")
    lines.append("- This is a block map, not yet proof that every block is user-visible text. FCEUX read/write tracing still needs to connect these offsets to specific runtime screens.")
    lines.append("- If expected entries such as `カタナ` do not match exactly under `+0x7A`, compare with the older offset-scan results in `candidate_region_decode.txt` and `kana_pattern_scan.txt`; some tables may use a related but shifted encoding.")
    lines.append("- In this watch range, shifted-low hits cluster around names/items, while the current `+0x7A` model only produces one exact translation-data match. Treat the shifted hits as breakpoint targets until runtime reads confirm the active table.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"blocks={len(blocks)} exact_matches={len(exact_matches)} watch_hits={len(translation_hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

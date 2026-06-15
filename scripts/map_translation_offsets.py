#!/usr/bin/env python3
"""Map translation_data entries to ROM offset candidates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from rom_utils import find_rom_path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_DATA = ROOT / "text_data" / "translation_data.txt"
OUT = ROOT / "rom_analysis" / "translation_offset_candidates.md"

PRG_HEADER = 0x10
PRG_SIZE = 0x20000
BANK1_ROM_START = 0x04010
BANK1_ROM_END = 0x08010
WATCH_ROM_START = 0x05610
WATCH_ROM_END = 0x05810

HIRAGANA_LOW = {
    "あ": 0x01, "い": 0x02, "う": 0x03, "え": 0x04, "お": 0x05,
    "か": 0x06, "き": 0x07, "く": 0x08, "け": 0x09, "こ": 0x0A,
    "さ": 0x0B, "し": 0x0C, "す": 0x0D, "せ": 0x0E, "そ": 0x0F,
    "た": 0x10, "ち": 0x11, "つ": 0x12, "て": 0x13, "と": 0x14,
    "な": 0x15, "に": 0x16, "ぬ": 0x17, "ね": 0x18, "の": 0x19,
    "は": 0x1A, "ひ": 0x1B, "ふ": 0x1C, "へ": 0x1D, "ほ": 0x1E,
    "ま": 0x20, "み": 0x21, "む": 0x22, "め": 0x23, "も": 0x24,
    "や": 0x25, "ゆ": 0x26, "よ": 0x27,
    "ら": 0x28, "り": 0x29, "る": 0x2A, "れ": 0x2B, "ろ": 0x2C,
    "わ": 0x2D, "を": 0x2E, "ん": 0x2F,
}

VOICED_TO_BASE = str.maketrans({
    "が": "か", "ぎ": "き", "ぐ": "く", "げ": "け", "ご": "こ",
    "ざ": "さ", "じ": "し", "ず": "す", "ぜ": "せ", "ぞ": "そ",
    "だ": "た", "ぢ": "ち", "づ": "つ", "で": "て", "ど": "と",
    "ば": "は", "び": "ひ", "ぶ": "ふ", "べ": "へ", "ぼ": "ほ",
    "ぱ": "は", "ぴ": "ひ", "ぷ": "ふ", "ぺ": "へ", "ぽ": "ほ",
})
KATAKANA_TO_HIRAGANA = str.maketrans(
    {chr(code): chr(code - 0x60) for code in range(ord("ァ"), ord("ヶ") + 1)}
)


@dataclass
class Entry:
    source: str
    korean: str
    category: str
    note: str
    normalized: str


@dataclass
class Hit:
    entry: Entry
    mode: str
    base: int
    encoded: bytes
    rom_offset: int

    @property
    def prg_offset(self) -> int:
        return self.rom_offset - PRG_HEADER

    @property
    def bank16(self) -> int:
        return self.prg_offset // 0x4000


def normalize(text: str, *, fold_voiced: bool) -> str:
    text = text.translate(KATAKANA_TO_HIRAGANA)
    if fold_voiced:
        text = text.translate(VOICED_TO_BASE)
    text = re.sub(r"[！!？?・ 　ー\-（）()0-9A-Za-z]", "", text)
    return text


def read_entries() -> list[Entry]:
    entries: list[Entry] = []
    for raw in TRANSLATION_DATA.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        while len(parts) < 4:
            parts.append("")
        normalized = normalize(parts[0], fold_voiced=True)
        if len(normalized) >= 2:
            entries.append(Entry(parts[0], parts[1], parts[2], parts[3], normalized))
    return entries


def encode_plus_7a(text: str) -> bytes | None:
    out = []
    for ch in normalize(text, fold_voiced=False):
        low = HIRAGANA_LOW.get(ch)
        if low is None:
            return None
        out.append(((0x100 + low) - 0x7A) & 0xFF)
    return bytes(out) if out else None


def encode_shifted_low(text: str, base: int) -> bytes | None:
    out = []
    for ch in normalize(text, fold_voiced=True):
        low = HIRAGANA_LOW.get(ch)
        if low is None:
            return None
        out.append((low + base) & 0xFF)
    return bytes(out) if out else None


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


def collect_hits(prg: bytes, entries: list[Entry]) -> list[Hit]:
    hits: list[Hit] = []
    for entry in entries:
        plus = encode_plus_7a(entry.source)
        if plus and len(plus) >= 2:
            for prg_offset in find_all(prg, plus):
                hits.append(Hit(entry, "plus-0x7A", 0x7A, plus, prg_offset + PRG_HEADER))

        for base in range(0x70, 0xA0):
            encoded = encode_shifted_low(entry.source, base)
            if not encoded or len(encoded) < 2:
                continue
            for prg_offset in find_all(prg, encoded):
                hits.append(Hit(entry, "shifted-low", base, encoded, prg_offset + PRG_HEADER))
    return hits


def fmt_bytes(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def hit_sort_key(hit: Hit):
    in_watch = WATCH_ROM_START <= hit.rom_offset < WATCH_ROM_END
    in_bank1 = BANK1_ROM_START <= hit.rom_offset < BANK1_ROM_END
    return (not in_watch, not in_bank1, hit.rom_offset, hit.entry.category, hit.entry.source, hit.mode, hit.base)


def section(lines: list[str], title: str, hits: list[Hit]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    if not hits:
        lines.append("No candidates.")
        lines.append("")
        return
    lines.append("| ROM offset | PRG offset | bank16 | mode | base | Japanese | Korean | category | bytes |")
    lines.append("| --- | --- | ---: | --- | --- | --- | --- | --- | --- |")
    for hit in sorted(hits, key=hit_sort_key):
        lines.append(
            f"| `0x{hit.rom_offset:05X}` | `0x{hit.prg_offset:05X}` | {hit.bank16} | "
            f"{hit.mode} | `0x{hit.base:02X}` | {hit.entry.source} | {hit.entry.korean} | "
            f"{hit.entry.category} | `{fmt_bytes(hit.encoded)}` |"
        )
    lines.append("")


def main() -> int:
    rom = Path(find_rom_path()).read_bytes()
    prg = rom[PRG_HEADER:PRG_HEADER + PRG_SIZE]
    entries = read_entries()
    hits = collect_hits(prg, entries)

    watch_hits = [hit for hit in hits if WATCH_ROM_START <= hit.rom_offset < WATCH_ROM_END]
    bank1_hits = [hit for hit in hits if BANK1_ROM_START <= hit.rom_offset < BANK1_ROM_END]
    plus_hits = [hit for hit in hits if hit.mode == "plus-0x7A"]

    lines: list[str] = []
    lines.append("# Translation offset candidates")
    lines.append("")
    lines.append("Generated by scanning `text_data/translation_data.txt` against PRG ROM.")
    lines.append("")
    lines.append("Encoding modes:")
    lines.append("")
    lines.append("- `plus-0x7A`: current hypothesis, `CHR tile = PRG byte + 0x7A`.")
    lines.append("- `shifted-low`: older offset-scan model, `PRG byte = hiragana_low + base`, with voiced kana folded to base kana.")
    lines.append("")
    lines.append(f"Total candidates: `{len(hits)}`")
    lines.append("")
    section(lines, "Matches inside ROM+0x05610-0x05810 watch range", watch_hits)
    section(lines, "Bank 1 matches (ROM+0x04010-0x08010)", sorted(bank1_hits, key=hit_sort_key)[:300])
    section(lines, "All plus-0x7A matches", sorted(plus_hits, key=hit_sort_key)[:300])
    lines.append("## Notes")
    lines.append("")
    lines.append("- The watch range currently has only a small number of exact translation-data matches; many blocks are likely encoded with controls, shifted tables, or non-hiragana tiles.")
    lines.append("- `shifted-low` hits are candidates, not proof. Use FCEUX runtime reads/writes to confirm which table is active on a given screen.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"hits={len(hits)} watch={len(watch_hits)} bank1={len(bank1_hits)} plus={len(plus_hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

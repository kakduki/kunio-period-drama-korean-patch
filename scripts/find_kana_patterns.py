#!/usr/bin/env python3
"""Search PRG ROM for kana-like byte patterns derived from CHR bank 07."""
from dataclasses import dataclass

from rom_utils import find_rom_path


HIRAGANA_TILE = {
    "あ": 0x101, "い": 0x102, "う": 0x103, "え": 0x104, "お": 0x105,
    "か": 0x106, "き": 0x107, "く": 0x108, "け": 0x109, "こ": 0x10A,
    "さ": 0x10B, "し": 0x10C, "す": 0x10D, "せ": 0x10E, "そ": 0x10F,
    "た": 0x110, "ち": 0x111, "つ": 0x112, "て": 0x113, "と": 0x114,
    "な": 0x115, "に": 0x116, "ぬ": 0x117, "ね": 0x118, "の": 0x119,
    "は": 0x11A, "ひ": 0x11B, "ふ": 0x11C, "へ": 0x11D, "ほ": 0x11E,
    "ま": 0x120, "み": 0x121, "む": 0x122, "め": 0x123, "も": 0x124,
    "や": 0x125, "ゆ": 0x126, "よ": 0x127,
    "ら": 0x128, "り": 0x129, "る": 0x12A, "れ": 0x12B, "ろ": 0x12C,
    "わ": 0x12D, "を": 0x12E, "ん": 0x12F,
}

VOICED_TO_BASE = {
    "が": "か", "ぎ": "き", "ぐ": "く", "げ": "け", "ご": "こ",
    "ざ": "さ", "じ": "し", "ず": "す", "ぜ": "せ", "ぞ": "そ",
    "だ": "た", "ぢ": "ち", "づ": "つ", "で": "て", "ど": "と",
    "ば": "は", "び": "ひ", "ぶ": "ふ", "べ": "へ", "ぼ": "ほ",
    "ぱ": "は", "ぴ": "ひ", "ぷ": "ふ", "ぺ": "へ", "ぽ": "ほ",
}

PATTERNS = [
    ("kunimasa", "くにまさ"),
    ("tsurumatsu", "つるまつ"),
    ("raifu", "らいふ"),
    ("chikara", "ちから"),
    ("ugoki", "うごき"),
    ("okane", "おかね"),
    ("mochimono", "もちもの"),
    ("taberu", "たべる"),
    ("suteru", "すてる"),
    ("konbou_base", "こんほう"),
    ("katana", "かたな"),
    ("yari", "やり"),
    ("kusuri", "くすり"),
    ("iikusuri", "いいくすり"),
    ("onigiri", "おにぎり"),
    ("tama", "たま"),
    ("mise", "みせ"),
    ("takara", "たから"),
    ("chizu", "ちず"),
    ("jidaigeki_base", "したいけき"),
]


@dataclass
class Hit:
    label: str
    text: str
    mode: str
    offset: int
    rom_offset: int
    prg_offset: int
    bank16: int
    bytes_hex: str
    context_hex: str
    score: int


def normalize_text(text: str) -> str:
    return "".join(VOICED_TO_BASE.get(ch, ch) for ch in text)


def encode_low_bytes(text: str, add: int = 0) -> bytes | None:
    out = []
    for ch in normalize_text(text):
        if ch not in HIRAGANA_TILE:
            return None
        out.append(((HIRAGANA_TILE[ch] & 0xFF) + add) & 0xFF)
    return bytes(out)


def find_all(haystack: bytes, needle: bytes):
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            return
        yield idx
        start = idx + 1


def make_hit(label: str, text: str, mode: str, offset: int, prg: bytes, idx: int, needle: bytes) -> Hit:
    ctx_start = max(0, idx - 8)
    ctx_end = min(len(prg), idx + len(needle) + 8)
    context = prg[ctx_start:ctx_end]
    delimiters = sum(1 for b in context if b in (0x00, 0xFF, 0xF0, 0xF8, 0xF9))
    score = len(needle) * 10 + delimiters
    return Hit(
        label=label,
        text=text,
        mode=mode,
        offset=offset,
        rom_offset=idx + 16,
        prg_offset=idx,
        bank16=idx // 0x4000,
        bytes_hex=" ".join(f"{b:02X}" for b in needle),
        context_hex=" ".join(f"{b:02X}" for b in context),
        score=score,
    )


with open(find_rom_path(), "rb") as f:
    data = f.read()

prg = data[16:16 + 131072]
hits: list[Hit] = []

for label, text in PATTERNS:
    direct = encode_low_bytes(text, 0)
    if direct:
        for idx in find_all(prg, direct):
            hits.append(make_hit(label, text, "direct-low-byte", 0, prg, idx, direct))

    # Offset scan checks whether the same contiguous kana ordering is present
    # under a different base code in PRG text data.
    for add in range(1, 256):
        encoded = encode_low_bytes(text, add)
        if not encoded:
            continue
        for idx in find_all(prg, encoded):
            hits.append(make_hit(label, text, "offset-low-byte", add, prg, idx, encoded))

print("=== Kana pattern scan from CHR bank 07 map ===")
print("Assumptions checked:")
print("- direct-low-byte: CHR tile 0x101 becomes text byte 0x01, etc.")
print("- offset-low-byte: same kana ordering, but shifted by a fixed byte offset.")
print("- voiced kana are normalized to their unvoiced base for this first pass.")
print()

if not hits:
    print("No matches found.")
else:
    print(f"Total hits: {len(hits)}")

    print("\n=== Offset summary for stronger hits (pattern length >= 3) ===")
    summary = {}
    for hit in hits:
        if len(bytes.fromhex(hit.bytes_hex.replace(" ", ""))) < 3:
            continue
        key = (hit.mode, hit.offset, hit.bank16)
        if key not in summary:
            summary[key] = {"count": 0, "labels": set(), "score": 0, "first": hit}
        summary[key]["count"] += 1
        summary[key]["labels"].add(hit.label)
        summary[key]["score"] += hit.score

    ranked = sorted(
        summary.items(),
        key=lambda item: (
            len(item[1]["labels"]),
            item[1]["count"],
            item[1]["score"],
        ),
        reverse=True,
    )
    for (mode, offset, bank16), item in ranked[:40]:
        labels = ",".join(sorted(item["labels"]))
        first = item["first"]
        print(
            f"{mode:16s} add=0x{offset:02X} bank16={bank16} "
            f"hits={item['count']:3d} labels={len(item['labels']):2d} "
            f"first=ROM+0x{first.rom_offset:05X} [{labels}]"
        )

    print("\n=== Strong detailed hits ===")
    strong_hits = [
        hit for hit in hits
        if len(bytes.fromhex(hit.bytes_hex.replace(" ", ""))) >= 3
    ]
    strong_hits.sort(key=lambda hit: (hit.score, len(hit.bytes_hex), -hit.rom_offset), reverse=True)
    for hit in strong_hits[:300]:
        print(
            f"{hit.label:14s} {hit.text:10s} score={hit.score:2d} "
            f"{hit.mode:16s} add=0x{hit.offset:02X} "
            f"ROM+0x{hit.rom_offset:05X} PRG+0x{hit.prg_offset:05X} "
            f"bank16={hit.bank16} bytes=[{hit.bytes_hex}] context=[{hit.context_hex}]"
        )

    if len(strong_hits) > 300:
        print(f"... {len(strong_hits) - 300} additional strong hits omitted")

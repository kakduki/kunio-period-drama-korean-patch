#!/usr/bin/env python3
"""Scan the ROM for kana patterns from the full translation reference.

This is a broad candidate finder. It is meant to discover likely menu/title/UI
offsets that are not covered by the current Bank 1 focused inventory.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from rom_utils import REPO_ROOT, find_rom_path


REFERENCE_JSON = REPO_ROOT / "text_data" / "translation_readable_reference.json"
STATUS_JSON = REPO_ROOT / "rom_analysis" / "bank1_offset_status.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "translation_pattern_scan.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "translation_pattern_scan.md"


KANA_TILE = {
    "あ": 0x101,
    "い": 0x102,
    "う": 0x103,
    "え": 0x104,
    "お": 0x105,
    "か": 0x106,
    "き": 0x107,
    "く": 0x108,
    "け": 0x109,
    "こ": 0x10A,
    "さ": 0x10B,
    "し": 0x10C,
    "す": 0x10D,
    "せ": 0x10E,
    "そ": 0x10F,
    "た": 0x110,
    "ち": 0x111,
    "つ": 0x112,
    "て": 0x113,
    "と": 0x114,
    "な": 0x115,
    "に": 0x116,
    "ぬ": 0x117,
    "ね": 0x118,
    "の": 0x119,
    "は": 0x11A,
    "ひ": 0x11B,
    "ふ": 0x11C,
    "へ": 0x11D,
    "ほ": 0x11E,
    "ま": 0x120,
    "み": 0x121,
    "む": 0x122,
    "め": 0x123,
    "も": 0x124,
    "や": 0x125,
    "ゆ": 0x126,
    "よ": 0x127,
    "ら": 0x128,
    "り": 0x129,
    "る": 0x12A,
    "れ": 0x12B,
    "ろ": 0x12C,
    "わ": 0x12D,
    "を": 0x12E,
    "ん": 0x12F,
}

VOICED_TO_BASE = {
    "が": "か",
    "ぎ": "き",
    "ぐ": "く",
    "げ": "け",
    "ご": "こ",
    "ざ": "さ",
    "じ": "し",
    "ず": "す",
    "ぜ": "せ",
    "ぞ": "そ",
    "だ": "た",
    "ぢ": "ち",
    "づ": "つ",
    "で": "て",
    "ど": "と",
    "ば": "は",
    "び": "ひ",
    "ぶ": "ふ",
    "べ": "へ",
    "ぼ": "ほ",
    "ぱ": "は",
    "ぴ": "ひ",
    "ぷ": "ふ",
    "ぺ": "へ",
    "ぽ": "ほ",
}

SMALL_TO_BASE = {
    "ぁ": "あ",
    "ぃ": "い",
    "ぅ": "う",
    "ぇ": "え",
    "ぉ": "お",
    "っ": "つ",
    "ゃ": "や",
    "ゅ": "ゆ",
    "ょ": "よ",
    "ゎ": "わ",
}

CATEGORY_GROUPS = {
    "타이틀": "title/menu",
    "메뉴": "title/menu",
    "모드": "title/menu",
    "UI": "ui/status",
    "능력치": "ui/status",
    "캐릭터명": "ui/status",
    "무기": "items/equipment",
    "방어구": "items/equipment",
    "소모품": "items/equipment",
    "특수": "items/equipment",
    "기술": "event/dialogue",
    "지역": "event/dialogue",
    "보스": "event/dialogue",
    "엔딩": "event/dialogue",
    "이벤트": "event/dialogue",
}


def katakana_to_hiragana(ch: str) -> str:
    code = ord(ch)
    if 0x30A1 <= code <= 0x30F6:
        return chr(code - 0x60)
    return ch


def normalize_source(text: str) -> str:
    out = []
    for ch in text:
        ch = katakana_to_hiragana(ch)
        ch = SMALL_TO_BASE.get(ch, ch)
        ch = VOICED_TO_BASE.get(ch, ch)
        if ch in KANA_TILE:
            out.append(ch)
    return "".join(out)


def encode(text: str, add: int) -> bytes | None:
    normalized = normalize_source(text)
    if len(normalized) < 3:
        return None
    return bytes((((KANA_TILE[ch] & 0xFF) + add) & 0xFF) for ch in normalized)


def find_all(data: bytes, needle: bytes):
    start = 0
    while True:
        idx = data.find(needle, start)
        if idx < 0:
            return
        yield idx
        start = idx + 1


def hex_bytes(raw: bytes) -> str:
    return " ".join(f"{b:02X}" for b in raw)


def score_hit(needle: bytes, context: bytes, category: str, known: bool) -> int:
    delimiters = sum(1 for b in context if b in {0x00, 0xFF, 0xF0, 0xF8, 0xF9})
    group_bonus = 25 if CATEGORY_GROUPS.get(category) == "title/menu" else 0
    known_penalty = -20 if known else 0
    return len(needle) * 10 + delimiters * 3 + group_bonus + known_penalty


def load_reference() -> list[dict[str, str]]:
    payload = json.loads(REFERENCE_JSON.read_text(encoding="utf-8"))
    return payload["translation_data_joined"]


def known_rom_hits() -> set[int]:
    payload = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
    hits = set()
    for row in payload.get("targets", []):
        raw = row.get("rom_hit", "")
        if raw:
            hits.add(int(str(raw), 16))
    for group in payload.get("groups", {}).values():
        for row in group.get("targets", []):
            raw = row.get("rom_hit", "")
            if raw:
                hits.add(int(str(raw), 16))
    return hits


def main() -> int:
    rom_path = find_rom_path(None)
    rom = rom_path.read_bytes()
    prg = rom[16 : 16 + 0x20000]
    known_hits = known_rom_hits()

    hits: list[dict[str, object]] = []
    skipped = []

    for entry in load_reference():
        source = entry["source"]
        normalized = normalize_source(source)
        if len(normalized) < 3:
            skipped.append({"source": source, "reason": "less than 3 encodable kana"})
            continue

        for add in range(256):
            needle = encode(source, add)
            if not needle:
                continue
            for prg_offset in find_all(prg, needle):
                rom_offset = prg_offset + 16
                context_start = max(0, prg_offset - 8)
                context_end = min(len(prg), prg_offset + len(needle) + 8)
                context = prg[context_start:context_end]
                known = rom_offset in known_hits
                row = {
                    "source": source,
                    "normalized": normalized,
                    "romaji": entry.get("romaji", ""),
                    "korean": entry.get("korean", ""),
                    "category": entry.get("category", ""),
                    "group": CATEGORY_GROUPS.get(entry.get("category", ""), "other"),
                    "rom_offset": f"0x{rom_offset:05X}",
                    "prg_offset": f"0x{prg_offset:05X}",
                    "bank16": prg_offset // 0x4000,
                    "add": f"0x{add:02X}",
                    "bytes": hex_bytes(needle),
                    "context": hex_bytes(context),
                    "known_bank1_target": known,
                    "score": score_hit(needle, context, entry.get("category", ""), known),
                }
                hits.append(row)

    hits.sort(key=lambda row: (row["score"], len(str(row["bytes"])), str(row["rom_offset"])), reverse=True)
    group_counts = Counter(row["group"] for row in hits)
    category_counts = Counter(row["category"] for row in hits)
    bank_counts = Counter(row["bank16"] for row in hits)

    new_hits = [row for row in hits if not row["known_bank1_target"]]
    menu_hits = [row for row in new_hits if row["group"] == "title/menu"]
    high_value = [row for row in new_hits if row["score"] >= 45]

    by_entry: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in new_hits:
        key = f"{row['source']}|{row['category']}"
        if len(by_entry[key]) < 5:
            by_entry[key].append(row)

    payload = {
        "source": {
            "rom": str(rom_path.relative_to(REPO_ROOT)),
            "reference": str(REFERENCE_JSON.relative_to(REPO_ROOT)),
            "known_bank1_targets": str(STATUS_JSON.relative_to(REPO_ROOT)),
        },
        "summary": {
            "reference_entries": len(load_reference()),
            "hits_total": len(hits),
            "new_hits_total": len(new_hits),
            "menu_title_new_hits": len(menu_hits),
            "high_value_new_hits": len(high_value),
            "skipped_entries": len(skipped),
        },
        "group_counts": dict(group_counts),
        "category_counts": dict(category_counts),
        "bank_counts": {str(k): v for k, v in sorted(bank_counts.items())},
        "top_new_hits": new_hits[:120],
        "top_menu_title_hits": menu_hits[:80],
        "top_known_hits": [row for row in hits if row["known_bank1_target"]][:40],
        "skipped": skipped,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Translation Pattern Scan",
        "",
        "Broad ROM scan from the full translation reference. This is candidate evidence only.",
        "",
        "## Summary",
        "",
        f"- Reference entries: **{payload['summary']['reference_entries']}**",
        f"- Total hits: **{payload['summary']['hits_total']}**",
        f"- New hits outside known Bank 1 targets: **{payload['summary']['new_hits_total']}**",
        f"- New title/menu hits: **{payload['summary']['menu_title_new_hits']}**",
        f"- High-value new hits: **{payload['summary']['high_value_new_hits']}**",
        "",
        "## Bank Distribution",
        "",
        "| 16KB bank | hits |",
        "| ---: | ---: |",
    ]
    for bank, count in sorted(bank_counts.items()):
        lines.append(f"| {bank} | {count} |")

    lines += [
        "",
        "## Top New Title/Menu Hits",
        "",
        "| score | source | korean | category | ROM | bank | add | bytes |",
        "| ---: | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in menu_hits[:40]:
        lines.append(
            f"| {row['score']} | {row['source']} | {row['korean']} | {row['category']} | "
            f"`{row['rom_offset']}` | {row['bank16']} | `{row['add']}` | `{row['bytes']}` |"
        )

    lines += [
        "",
        "## Top New Hits",
        "",
        "| score | group | source | korean | category | ROM | bank | add | bytes |",
        "| ---: | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in new_hits[:60]:
        lines.append(
            f"| {row['score']} | {row['group']} | {row['source']} | {row['korean']} | "
            f"{row['category']} | `{row['rom_offset']}` | {row['bank16']} | `{row['add']}` | `{row['bytes']}` |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- Katakana and voiced kana are normalized to the existing kana tile order before scanning.",
        "- A hit is not patch approval; it becomes useful when a screen dump confirms the active bank/context.",
        "- Title/menu hits are prioritized because the current Bank 1 status has no menu-category targets.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        "hits={hits_total} new={new_hits_total} menu={menu_title_new_hits} high={high_value_new_hits}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Readable display labels for candidate text where source files are mojibake."""

from __future__ import annotations


READABLE_BY_ROMAJI = {
    "Hashi": {
        "source_display": "はし",
        "korean_display": "다리",
        "meaning": "stage/location label",
        "screen_hint": "look for a bridge/stage/location label",
    },
    "Heishichi": {
        "source_display": "へいしち",
        "korean_display": "헤이시치",
        "meaning": "name/dialogue label",
        "screen_hint": "look for a visible Heishichi name/dialogue context",
    },
    "Kajiya": {
        "source_display": "かじや",
        "korean_display": "대장간",
        "meaning": "blacksmith/stage label",
        "screen_hint": "look for a blacksmith/shop or blacksmith-stage label",
    },
    "Katana": {
        "source_display": "かたな",
        "korean_display": "카타나",
        "meaning": "weapon/item label",
        "screen_hint": "look for a katana/weapon item label",
    },
    "Raifu": {
        "source_display": "ライフ",
        "korean_display": "라이프",
        "meaning": "UI life label",
        "screen_hint": "look for a life/status UI label",
    },
    "Tatsuichi": {
        "source_display": "たついち",
        "korean_display": "타츠이치",
        "meaning": "name/dialogue label",
        "screen_hint": "look for a visible Tatsuichi name/dialogue context",
    },
    "Tatsuji": {
        "source_display": "たつじ",
        "korean_display": "타츠지",
        "meaning": "boss/name label",
        "screen_hint": "look for a visible Tatsuji boss/name context",
    },
}


def readable_for_romaji(romaji: object) -> dict[str, str]:
    return dict(READABLE_BY_ROMAJI.get(str(romaji), {}))


def enrich_with_readable(row: dict[str, object], romaji_key: str = "romaji") -> dict[str, object]:
    enriched = dict(row)
    readable = readable_for_romaji(enriched.get(romaji_key, ""))
    for key, value in readable.items():
        enriched.setdefault(key, value)
    return enriched

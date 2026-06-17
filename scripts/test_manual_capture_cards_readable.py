#!/usr/bin/env python3
"""Check that manual capture cards use human-readable labels."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


CARDS_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_cards.json"
CARDS_MD = REPO_ROOT / "rom_analysis" / "manual_capture_cards.md"


EXPECTED_LABELS = {
    "Katana": ("かたな", "카타나"),
    "Kajiya": ("かじや", "대장간"),
    "Tatsuji": ("たつじ", "타츠지"),
}


def main() -> int:
    payload = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
    cards = payload.get("cards", [])
    errors: list[str] = []

    if not cards:
        errors.append("manual capture cards are empty")

    by_romaji = {card.get("romaji"): card for card in cards if card.get("romaji")}
    for romaji, (source, korean) in EXPECTED_LABELS.items():
        card = by_romaji.get(romaji)
        if not card:
            errors.append(f"{romaji} card is missing")
            continue
        if card.get("source_display") != source:
            errors.append(f"{romaji} source_display is {card.get('source_display')!r}, expected {source!r}")
        if card.get("korean_display") != korean:
            errors.append(f"{romaji} korean_display is {card.get('korean_display')!r}, expected {korean!r}")
        if not card.get("screen_hint"):
            errors.append(f"{romaji} screen_hint is missing")

    markdown = CARDS_MD.read_text(encoding="utf-8")
    for expected in ["かたな -> 카타나", "かじや -> 대장간", "たつじ -> 타츠지"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown cards")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: manual capture cards use readable display labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

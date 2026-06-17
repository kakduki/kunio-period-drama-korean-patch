#!/usr/bin/env python3
"""Extract a readable Japanese/romaji reference from the transcription file."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = ROOT / "text_data"
TRANSLATION_DATA = TEXT_DIR / "translation_data.txt"
OUT_MD = TEXT_DIR / "translation_readable_reference.md"
OUT_JSON = TEXT_DIR / "translation_readable_reference.json"

BASE_KANA = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "を": "wo", "ん": "n",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
    "ー": "-",
}
YOON = {
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",
    "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",
    "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",
    "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
    "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
    "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
    "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
    "びゃ": "bya", "びゅ": "byu", "びょ": "byo",
    "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
}


def find_transcription() -> Path:
    candidates = [
        path
        for path in TEXT_DIR.glob("*.md")
        if path.name != "source_notes.md" and path.name != OUT_MD.name
    ]
    if len(candidates) != 1:
        names = ", ".join(path.name for path in candidates)
        raise RuntimeError(f"Expected one transcription markdown file, found {len(candidates)}: {names}")
    return candidates[0]


def parse_transcription(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    section = ""
    subsection = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            subsection = ""
            continue
        if line.startswith("### "):
            subsection = line[4:].strip()
            continue
        if not line.startswith("|") or "---" in line:
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 3 or parts[0] in {"텍스트", "?띿뒪??"} or parts[1] in {"읽기", "?쎄린"}:
            continue
        entries.append(
            {
                "source": parts[0],
                "romaji": parts[1],
                "note": parts[2],
                "section": section,
                "subsection": subsection,
            }
        )
    return entries


def parse_translation_data() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw in TRANSLATION_DATA.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        while len(parts) < 4:
            parts.append("")
        entries.append(
            {
                "source": parts[0],
                "korean": parts[1],
                "category": parts[2],
                "note": parts[3],
            }
        )
    return entries


def kana_to_romaji(text: str) -> str:
    out: list[str] = []
    small_tsu = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "っ":
            small_tsu = True
            index += 1
            continue
        if text[index:index + 2] in YOON:
            syllable = YOON[text[index:index + 2]]
            index += 2
        else:
            syllable = BASE_KANA.get(char, char)
            index += 1
        if small_tsu and syllable and syllable[0].isalpha():
            syllable = syllable[0] + syllable
        small_tsu = False
        out.append(syllable)
    return "".join(out).replace("-", "")


def fill_missing_romaji(row: dict[str, str]) -> dict[str, str]:
    filled = dict(row)
    source = filled.get("source", "")
    romaji = kana_to_romaji(source)
    display_romaji = romaji[:1].upper() + romaji[1:] if romaji else ""
    filled.update(
        {
            "romaji": display_romaji,
            "transcription_note": "auto-romaji fallback from translation_data source",
            "section": "translation_data fallback",
            "subsection": filled.get("category", ""),
            "romaji_source": "auto-kana",
        }
    )
    return filled


def main() -> int:
    transcription_path = find_transcription()
    reference = parse_transcription(transcription_path)
    by_source = {entry["source"]: entry for entry in reference}
    translations = parse_translation_data()

    matched = []
    fallback = []
    missing = []
    for entry in translations:
        ref = by_source.get(entry["source"])
        row = dict(entry)
        if ref:
            row.update(
                {
                    "romaji": ref["romaji"],
                    "transcription_note": ref["note"],
                    "section": ref["section"],
                    "subsection": ref["subsection"],
                }
            )
            matched.append(row)
        elif any("\u3040" <= char <= "\u309f" for char in entry["source"]):
            row = fill_missing_romaji(row)
            matched.append(row)
            fallback.append(row)
        else:
            missing.append(row)

    payload = {
        "source": {
            "transcription": str(transcription_path.relative_to(ROOT)),
            "translation_data": str(TRANSLATION_DATA.relative_to(ROOT)),
        },
        "summary": {
            "transcription_entries": len(reference),
            "translation_entries": len(translations),
            "translation_entries_with_romaji": len(matched),
            "translation_entries_auto_romaji": len(fallback),
            "translation_entries_missing_romaji": len(missing),
        },
        "reference": reference,
        "translation_data_joined": matched,
        "translation_data_missing": missing,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Translation Readable Reference",
        "",
        f"- Transcription source: `{transcription_path.relative_to(ROOT)}`",
        f"- Translation data source: `{TRANSLATION_DATA.relative_to(ROOT)}`",
        f"- Transcription entries: **{len(reference)}**",
        f"- Translation entries with romaji: **{len(matched)} / {len(translations)}**",
        f"- Auto-romaji fallback entries: **{len(fallback)}**",
        "",
        "## Translation Data Join",
        "",
        "| Japanese | romaji | Korean | category | transcription context |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in matched:
        context = row["subsection"] or row["section"]
        lines.append(
            f"| {row['source']} | {row['romaji']} | {row['korean']} | {row['category']} | {context} |"
        )

    if missing:
        lines += [
            "",
            "## Missing Romaji",
            "",
            "| Japanese | Korean | category |",
            "| --- | --- | --- |",
        ]
        for row in missing:
            lines.append(f"| {row['source']} | {row['korean']} | {row['category']} |")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        "transcription_entries={transcription_entries} translation_with_romaji={translation_entries_with_romaji}/{translation_entries}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

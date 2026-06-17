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


def main() -> int:
    transcription_path = find_transcription()
    reference = parse_transcription(transcription_path)
    by_source = {entry["source"]: entry for entry in reference}
    translations = parse_translation_data()

    matched = []
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

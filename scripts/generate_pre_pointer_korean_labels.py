#!/usr/bin/env python3
"""Generate a reviewable Korean label map for English pre-pointer records.

The English patch stores many short labels in a fixed FF-delimited Bank 1
block.  This script deliberately separates translation source and confidence:
known gameplay labels use a curated map, while character and place names use a
small romaji-to-Hangul fallback.  The output is a candidate input for a soft
gate ROM build, not a release translation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_SCRIPT = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_DIRECT_LABELS = REPO_ROOT / "text_data" / "direct_low_korean_labels.json"
DEFAULT_GLOSSARY = REPO_ROOT / "text_data" / "translation_readable_reference.json"
DEFAULT_OUTPUT = REPO_ROOT / "text_data" / "pre_pointer_korean_labels.json"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "pre_pointer_label_generation.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pre_pointer_label_generation.md"

TOKEN_RE = re.compile(r"<([0-9A-Fa-f]{2})>")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")

# These are intentionally short labels.  The fixed records are often used in
# compact menus, so a literal long explanatory translation is not appropriate.
ALIASES = {
    "SCREW": "\ud68c",
    "TORNADO": "\ud68c\uc624\ub9ac",
    "HELICPTR": "\ud5ec\uae30",
    "DRILL": "\ub4dc\ub9b4",
    "SLAP": "\ub54c\ub9ac",
    "DAGGR": "\ub2e8\uac80",
    "HEADBUTT": "\ubc15\uce58\uae30",
    "BMPKNART": "\uae30\uc220",
    "MASSAGE": "\uc548\ub9c8",
    "BIGBANG": "\ube45\ubc45",
    "WARPSHOT": "\uc6cc\ud504\uc298",
    "DEFLECT": "\ud68c",
    "KIUKIU": "\ud0a4\ud0a4",
    "SWING": "\ud68c\uc804",
    "PICKLE": "\ud53c\ud074",
    "MEAL": "\uc2dd\uc0ac",
    "SOBA": "\uc18c\ubc14",
    "UDON": "\uc6b0\ub3d9",
    "SOUP": "\uc218\ud504",
    "IMO": "\uac10\uc790",
    "FISH": "\uc0dd\uc120",
    "TENPURA": "\ud280\uae40",
    "DANGO": "\ub2f9\uace0",
    "RICEBALL": "\uc8fc\uba39\ubc25",
    "MANJUU": "\ub9cc\uc8fc",
    "SUSHI": "\ucd08\ubc25",
    "SALVE": "\uc5f0\uace0",
    "POULTICE": "\uc2b5\ud3ec",
    "TONIC": "\uac15\uc7a5\uc81c",
    "TOYAMA": "\ub3c4\uc57c\ub9c8",
    "ELIXIR": "\uc601\uc57d",
    "COTTON": "\uba74",
    "LONG": "\uae34",
    "OBSCENE": "\uc678\uc124",
    "COMMON": "\ubcf4\ud1b5",
    "WIDE": "\ub113\uc740",
    "THICK": "\ub450\uaebc\uc6b4",
    "WHITE": "\ud770\uc0c9",
    "SUN": "\ud574",
    "PRICEY": "\ube44\uc308",
    "SILK": "\ube44\ub2e8",
    "SAUCY": "\uac74\ubc29",
    "NARITA": "\ub098\ub9ac\ud0c0",
    "JET": "\uc81c\ud2b8",
    "SOFT": "\ubd80\ub4dc\ub7ec",
    "WOOL": "\uc591\ubaa8",
    "TWISTED": "\uaf2c\uc784",
    "PONGEE": "\uba85\uc8fc",
    "DOUBLEUP": "\ub450\ubc30",
    "SNOW": "\ub208",
    "SPIKED": "\uac00\uc2dc",
    "CAMEL": "\ub099\ud0c0",
    "KAPPA": "\uce87\ud30c",
    "MAGIC": "\ub9c8\ubc95",
    "SANKI": "\uc0b0\ud0a4",
    "CRSR": "\ucee4\uc11c",
    "MYSTERY": "\uc218\uc218\uaed8\ub07c",
    "GOODTIME": "\uc88b\uc740\ub54c",
    "EFFECT": "\ud6a8\uacfc",
    "MASTER": "\ub2ec\uc778",
    "JUMP": "\uc810\ud504",
    "RAINCOAT": "\uc6b0\ube44",
    "STAM": "\uae30\ub825",
    "VIT": "\uccb4\ub825",
    "PUNCH": "\ud380\uce58",
    "KICK": "\ud0a4\ud06c",
    "WPN": "\ubb34\uae30",
    "THROW": "\ub358\uc9c0\uae30",
    "AGI": "\ubbfc\ucca9",
    "WILL": "\uc758\uc9c0",
    "DEF": "\ubc29\uc5b4",
    "STR": "\ud798",
    "SURUGA": "\uc2a4\ub8e8\uac00",
    "KOUZ": "\ucf54\uc988\ucf00",
    "RIKUC": "\ub9ac\ucfe0",
    "ECCHU": "\uc5e3\ucd94",
    "INA": "\uc774\ub098",
    "KAW": "\uce74\uc640",
    "TO": "\ud1a0",
    "NAG": "\ub098\uac00",
    "HIZ": "\ud788\uc988",
    "ODD": "\uc624\ub4dc",
    "Z": "\uc988",
}


MORA = {
    "KYA": "\ucf04", "KYU": "\ud050", "KYO": "\uad50",
    "SHA": "\uc0e4", "SHU": "\uc288", "SHO": "\uc1fc",
    "CHA": "\ucc28", "CHU": "\ucd94", "CHO": "\ucd08",
    "NYA": "\ub0d0", "NYU": "\ub274", "NYO": "\ub1e8",
    "HYA": "\ud5e4\uc57c", "HYU": "\ud734", "HYO": "\ud6a8",
    "MYA": "\ubb18", "MYU": "\ubb18", "MYO": "\ubb18",
    "RYA": "\ub7b4", "RYU": "\ub958", "RYO": "\ub8cc",
    "TSU": "\uce20", "TCHI": "\uce58", "CHI": "\uce58",
    "SHI": "\uc2dc", "JI": "\uc9c0", "FU": "\ud6c4",
    "KA": "\uce74", "KI": "\ud0a4", "KU": "\ucfe0", "KE": "\ucf00", "KO": "\ucf54",
    "GA": "\uac00", "GI": "\uae30", "GU": "\uad6c", "GE": "\uac8c", "GO": "\uace0",
    "SA": "\uc0ac", "SI": "\uc2dc", "SU": "\uc218", "SE": "\uc138", "SO": "\uc18c",
    "ZA": "\uc790", "ZI": "\uc9c0", "ZU": "\uc988", "ZE": "\uc81c", "ZO": "\uc870",
    "TA": "\ud0c0", "TI": "\ud2f0", "TU": "\ud22c", "TE": "\ud14c", "TO": "\ud1a0",
    "DA": "\ub2e4", "DI": "\ub514", "DU": "\ub450", "DE": "\ub370", "DO": "\ub3c4",
    "NA": "\ub098", "NI": "\ub2c8", "NU": "\ub204", "NE": "\ub124", "NO": "\ub178",
    "HA": "\ud558", "HI": "\ud788", "HU": "\ud6c4", "HE": "\ud5e4", "HO": "\ud638",
    "BA": "\ubc14", "BI": "\ube44", "BU": "\ubd80", "BE": "\ubca0", "BO": "\ubcf4",
    "PA": "\ud30c", "PI": "\ud53c", "PU": "\ud478", "PE": "\ud398", "PO": "\ud3ec",
    "MA": "\ub9c8", "MI": "\ubbf8", "MU": "\ubb34", "ME": "\uba54", "MO": "\ubaa8",
    "YA": "\uc57c", "YU": "\uc720", "YO": "\uc694",
    "RA": "\ub77c", "RI": "\ub9ac", "RU": "\ub8e8", "RE": "\ub808", "RO": "\ub85c",
    "WA": "\uc640", "WO": "\uc624",
    "A": "\uc544", "I": "\uc774", "U": "\uc6b0", "E": "\uc5d0", "O": "\uc624",
}


def normalize_key(value: str) -> str:
    return re.sub(r"[^A-Z]", "", value.upper())


def plain_key(en_text: str) -> tuple[str | None, list[int]]:
    controls = [int(match.group(1), 16) for match in TOKEN_RE.finditer(en_text) if match.group(1).upper() != "FF"]
    if controls:
        return None, controls
    key = TOKEN_RE.sub("", en_text).replace("<FF>", "")
    return (normalize_key(key) or None), []


def transliterate(value: str) -> str:
    text = normalize_key(value)
    output: list[str] = []
    index = 0
    while index < len(text):
        if index + 1 < len(text) and text[index] == text[index + 1] and text[index] not in "AEIOU":
            index += 1
        match = next((size for size in (4, 3, 2, 1) if text[index : index + size] in MORA), None)
        if match is None:
            index += 1
            continue
        output.append(MORA[text[index : index + match]])
        index += match
    return "".join(output)


def load_direct_labels(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return {normalize_key(str(key)): str(value) for key, value in payload.items()}


def load_glossary(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    result: dict[str, str] = {}
    for item in payload.get("reference", []):
        key = normalize_key(str(item.get("romaji", "")))
        note = str(item.get("note", ""))
        if key and HANGUL_RE.search(note):
            result.setdefault(key, note.split("(", 1)[0].strip())
    return result


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [row for row in csv.DictReader(handle, delimiter="\t") if row["record_id"].startswith("EN-PRE-")]


def generate(script_path: Path, direct_labels_path: Path, glossary_path: Path, output_path: Path, report_json: Path, report_markdown: Path) -> dict[str, object]:
    direct_labels = load_direct_labels(direct_labels_path)
    glossary = load_glossary(glossary_path)
    records: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    for row in load_rows(script_path):
        key, controls = plain_key(row["en_text"])
        record: dict[str, object] = {
            "record_id": row["record_id"],
            "rom_offset": row["en_rom_offset"],
            "english_text": row["en_text"],
            "raw_bytes": row["en_raw_bytes"],
            "context": row["context"],
            "normalized_key": key or "",
            "control_bytes": [f"0x{value:02X}" for value in controls],
            "korean_text": "",
            "source": "",
            "confidence": "",
            "patch_ready": False,
        }
        if controls:
            record["source"] = "control_skeleton"
            record["confidence"] = "blocked"
        elif not key:
            record["source"] = "empty_or_data"
            record["confidence"] = "blocked"
        else:
            korean = ALIASES.get(key)
            source = "curated_alias"
            confidence = "reviewed_label"
            if korean is None and key in direct_labels:
                korean = direct_labels[key]
                source = "direct_low_label"
                confidence = "existing_candidate"
            if korean is None and key in glossary:
                korean = glossary[key]
                source = "translation_glossary_note"
                confidence = "glossary_semantic"
            if korean is None:
                korean = transliterate(key)
                source = "romaji_fallback"
                confidence = "fallback_name"
            record["korean_text"] = korean
            record["source"] = source
            record["confidence"] = confidence
            record["patch_ready"] = bool(korean)
        counts[str(record["confidence"])] = counts.get(str(record["confidence"]), 0) + 1
        records.append(record)

    payload = {
        "status": "GENERATED_SOFT_GATE_LABEL_MAP",
        "source_script": str(script_path),
        "record_count": len(records),
        "counts": counts,
        "records": records,
        "notes": [
            "Control-bearing and data-like records remain in the report but are not patch-ready.",
            "Fallback names are transliterations and require a later semantic review.",
            "The ROM builder independently checks glyph availability, width, and overlap.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Pre-Pointer Korean Label Generation",
        "",
        f"- Records inspected: `{len(records)}`.",
        f"- Patch-ready before font/width checks: `{sum(1 for row in records if row['patch_ready'])}`.",
        "- This is a soft-gate label inventory; it does not prove that every row is reached by the game.",
        "",
        "| record | offset | key | Korean | source | confidence | controls |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in records:
        lines.append(
            f"| {row['record_id']} | `{row['rom_offset']}` | {row['normalized_key']} | {row['korean_text']} | {row['source']} | {row['confidence']} | {','.join(row['control_bytes'])} |"
        )
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--direct-labels", type=Path, default=DEFAULT_DIRECT_LABELS)
    parser.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()
    payload = generate(args.script.resolve(), args.direct_labels.resolve(), args.glossary.resolve(), args.output.resolve(), args.report_json.resolve(), args.report_markdown.resolve())
    print(json.dumps({"status": payload["status"], "counts": payload["counts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

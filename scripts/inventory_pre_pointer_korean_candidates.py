#!/usr/bin/env python3
"""Inventory English pre-pointer/name records without promoting unsafe patches.

The English reference contains a fixed-bank record family that is separate
from the relocated pointer dialogue.  This tool joins only exact romanized
matches to the existing Korean glossary and reports the remaining evidence
needed before a record can be changed.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

try:
    from rom_utils import REPO_ROOT
except ModuleNotFoundError:
    from scripts.rom_utils import REPO_ROOT


DEFAULT_SCRIPT = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_GLOSSARY = REPO_ROOT / "text_data" / "translation_readable_reference.json"
DEFAULT_DIRECT_LABELS = REPO_ROOT / "text_data" / "direct_low_korean_labels.json"
DEFAULT_SLOT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
DEFAULT_EXPANSION_PLAN = REPO_ROOT / "rom_analysis" / "next_glyph_expansion_plan.json"
DEFAULT_OUTPUT_CSV = REPO_ROOT / "rom_analysis" / "pre_pointer_korean_candidates.csv"
DEFAULT_OUTPUT_JSON = REPO_ROOT / "rom_analysis" / "pre_pointer_korean_candidates.json"
DEFAULT_OUTPUT_MD = REPO_ROOT / "rom_analysis" / "pre_pointer_korean_candidates.md"

FRAME_883_TARGETS = {
    0x0561A,
    0x0562F,
    0x05643,
    0x0569D,
    0x056DA,
    0x0571C,
    0x057D4,
    0x0736A,
    0x0739D,
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize_romaji(value: str) -> str:
    return "".join(char for char in value.upper() if "A" <= char <= "Z")


def decode_english_text(value: str) -> str:
    """Remove explicit control tokens from the already decoded reference text."""

    return re.sub(r"<[^>]*>", "", value)


def parse_bytes(value: str) -> bytes:
    return bytes(int(part, 16) for part in value.split())


def parse_offset(value: str) -> int:
    return int(value, 16)


def build_glossary(glossary_path: Path, direct_labels_path: Path) -> dict[str, tuple[str, str]]:
    glossary = load_json(glossary_path)
    assert isinstance(glossary, dict)
    result: dict[str, tuple[str, str]] = {}
    for row in glossary.get("translation_data_joined", []):
        if not isinstance(row, dict):
            continue
        key = normalize_romaji(str(row.get("romaji", "")))
        korean = str(row.get("korean", "")).strip()
        if key and korean:
            result.setdefault(key, (korean, "translation_data_joined"))

    direct_labels = load_json(direct_labels_path)
    assert isinstance(direct_labels, dict)
    for english, korean in direct_labels.items():
        key = normalize_romaji(str(english))
        if key and str(korean).strip():
            result.setdefault(key, (str(korean).strip(), "direct_low_korean_labels"))
    return result


def build_glyph_codes(slot_plan_path: Path, expansion_plan_path: Path) -> dict[str, int]:
    slot_plan = load_json(slot_plan_path)
    expansion_plan = load_json(expansion_plan_path)
    assert isinstance(slot_plan, dict)
    assert isinstance(expansion_plan, dict)
    result: dict[str, int] = {}
    for row in slot_plan.get("slots", []):
        if not isinstance(row, dict):
            continue
        glyph = str(row.get("glyph", ""))
        code = row.get("prg_plus_0x7a_byte")
        if glyph and code:
            result[glyph] = int(str(code), 16)
    for row in expansion_plan.get("next_slots", [])[:46]:
        if not isinstance(row, dict):
            continue
        glyph = str(row.get("glyph", ""))
        code = row.get("prg_plus_0x7a_byte")
        if glyph and code:
            result.setdefault(glyph, int(str(code), 16))
    return result


def inventory(script_path: Path, glossary_path: Path, direct_labels_path: Path,
              slot_plan_path: Path, expansion_plan_path: Path) -> list[dict[str, object]]:
    glossary = build_glossary(glossary_path, direct_labels_path)
    glyph_codes = build_glyph_codes(slot_plan_path, expansion_plan_path)
    rows: list[dict[str, object]] = []
    with script_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            if source.get("source_language") != "english":
                continue
            if source.get("record_kind") != "ff_delimited":
                continue
            context = str(source.get("context", ""))
            if "pre-pointer" not in context and "name-table" not in context:
                continue

            raw = parse_bytes(str(source.get("en_raw_bytes", "")))
            ff_index = raw.find(b"\xFF")
            payload = raw if ff_index < 0 else raw[:ff_index]
            decoded = decode_english_text(str(source.get("en_text", "")))
            key = normalize_romaji(decoded)
            glossary_row = glossary.get(key)
            korean = glossary_row[0] if glossary_row else ""
            source_kind = glossary_row[1] if glossary_row else ""
            korean_chars = [char for char in korean if not char.isspace()]
            missing_glyphs = sorted({char for char in korean_chars if char not in glyph_codes})
            encoded = bytes(glyph_codes[char] for char in korean_chars) if not missing_glyphs else b""
            control_bytes = [value for value in payload if not 0x81 <= value <= 0x9A]
            offset = parse_offset(str(source.get("en_rom_offset")))
            exact_frame_target = offset in FRAME_883_TARGETS
            length_ok = bool(encoded) and len(encoded) <= len(payload) and not control_bytes
            evidence = "frame-883-target" if exact_frame_target else "none"
            if offset == 0x05BDF:
                evidence = "source-reachability-only"
            if missing_glyphs:
                readiness = "BLOCKED_MISSING_GLYPH"
            elif not glossary_row:
                readiness = "UNMAPPED_GLOSSARY"
            elif control_bytes:
                readiness = "BLOCKED_CONTROL_SKELETON"
            elif not encoded:
                readiness = "BLOCKED_EMPTY_ENCODING"
            elif len(encoded) > len(payload):
                readiness = "BLOCKED_LENGTH_OVERFLOW"
            elif not exact_frame_target:
                readiness = "MAPPED_RUNTIME_UNKNOWN"
            else:
                readiness = "FRAME_TARGET_READY_FOR_VISUAL_PATCH"
            rows.append({
                "record_id": source.get("record_id", ""),
                "context": context,
                "rom_offset": f"0x{offset:05X}",
                "raw_bytes": raw.hex(" ").upper(),
                "english_text": source.get("en_text", ""),
                "normalized_key": key,
                "korean_text": korean,
                "translation_source": source_kind,
                "payload_length": len(payload),
                "korean_length": len(encoded),
                "length_delta": len(encoded) - len(payload) if encoded else "",
                "control_bytes": " ".join(f"0x{x:02X}" for x in control_bytes),
                "missing_glyphs": "".join(missing_glyphs),
                "runtime_evidence": evidence,
                "readiness": readiness,
                "patch_authorized": readiness == "FRAME_TARGET_READY_FOR_VISUAL_PATCH",
            })
    return rows


def write_outputs(rows: list[dict[str, object]], output_csv: Path, output_json: Path, output_md: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    output_json.write_text(json.dumps({"rows": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["readiness"])
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "# Pre-Pointer Korean Candidate Inventory",
        "",
        "This is an ownership and readiness inventory. It does not authorize a broad text replacement.",
        "",
        f"- Records: **{len(rows)}**.",
        f"- Exact frame-883 records: **{sum(bool(row['patch_authorized']) for row in rows)}**.",
        "- Existing English pre-pointer records are kept separate from relocated pointer dialogue.",
        "",
        "## Readiness",
        "",
        "| status | count |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{status}` | {count} |" for status, count in sorted(counts.items()))
    lines += [
        "",
        "## Interpretation",
        "",
        "Exact glossary matches are still not sufficient for release: the renderer must be visually checked, and control-bearing records remain blocked even when a Korean wording exists.",
        "The CSV is the next queue for targeted FCEUX routes.",
        "",
    ]
    output_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    parser.add_argument("--direct-labels", type=Path, default=DEFAULT_DIRECT_LABELS)
    parser.add_argument("--slot-plan", type=Path, default=DEFAULT_SLOT_PLAN)
    parser.add_argument("--expansion-plan", type=Path, default=DEFAULT_EXPANSION_PLAN)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()
    rows = inventory(args.script, args.glossary, args.direct_labels, args.slot_plan, args.expansion_plan)
    write_outputs(rows, args.output_csv, args.output_json, args.output_md)
    print(json.dumps({
        "records": len(rows),
        "frame_target_ready": sum(bool(row["patch_authorized"]) for row in rows),
        "output_csv": str(args.output_csv),
        "output_json": str(args.output_json),
        "output_md": str(args.output_md),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

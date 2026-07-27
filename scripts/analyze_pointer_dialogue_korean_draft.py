#!/usr/bin/env python3
"""Audit the full Korean pointer-dialogue draft before ROM compilation.

The English reference supplies record ownership and control boundaries. This
audit measures the Korean draft against the currently proven direct dialogue
font pool and reports why a full build is or is not eligible for promotion.
It intentionally does not patch a ROM.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from rom_utils import REPO_ROOT


POINTER_COUNT = 248
# The English reference establishes 0x81-0x9A. The bounded opening p182
# capacity proof also observed 0xC0-0xC7 through the same paired renderer.
# This is an opening-context proof, not a release-wide guarantee.
PROVEN_SOURCE_CODES = tuple(range(0x81, 0x9B)) + tuple(range(0xC0, 0xC8))
POINTER_RECORD_START = 0x05FE7
POINTER_RECORD_LIMIT = 0x08010
DEFAULT_DRAFT = REPO_ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv"
DEFAULT_ENGLISH = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "pointer_dialogue_korean_draft_report.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pointer_dialogue_korean_draft_report.md"


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate_draft(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if len(rows) != POINTER_COUNT:
        raise ValueError(f"expected {POINTER_COUNT} draft rows, found {len(rows)}")
    indices = [int(row["pointer_index"]) for row in rows]
    if indices != list(range(POINTER_COUNT)):
        raise ValueError("draft rows must contain pointer indices 0..247 in order")
    required = {"translation_status", "korean_text", "basis", "notes"}
    for row in rows:
        missing = required - set(row)
        if missing:
            raise ValueError(f"pointer {row['pointer_index']} is missing {sorted(missing)}")
    return rows


def english_pointer_rows(rows: list[dict[str, str]]) -> dict[int, dict[str, str]]:
    pointer_rows = [row for row in rows if row.get("record_kind") == "pointer_pair"]
    if len(pointer_rows) != POINTER_COUNT:
        raise ValueError(f"expected {POINTER_COUNT} English pointer rows, found {len(pointer_rows)}")
    return {int(row["pointer_index"]): row for row in pointer_rows}


def active_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if not row["translation_status"].startswith("excluded")]


def used_symbols(rows: list[dict[str, str]]) -> set[str]:
    return {character for row in active_rows(rows) for character in row["korean_text"] if character != " "}


def estimated_length(text: str) -> int:
    # F0 BB 00 is the conservative generic dialogue prefix; spaces are 00.
    return 4 + len(text)


def sequential_batches(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    batches: list[dict[str, object]] = []
    current_indices: list[int] = []
    current_symbols: set[str] = set()
    for row in active_rows(rows):
        index = int(row["pointer_index"])
        symbols = {character for character in row["korean_text"] if character != " "}
        if current_indices and len(current_symbols | symbols) > len(PROVEN_SOURCE_CODES):
            batches.append(
                {
                    "pointer_indices": current_indices,
                    "record_count": len(current_indices),
                    "unique_symbols": len(current_symbols),
                }
            )
            current_indices = []
            current_symbols = set()
        current_indices.append(index)
        current_symbols.update(symbols)
    if current_indices:
        batches.append(
            {
                "pointer_indices": current_indices,
                "record_count": len(current_indices),
                "unique_symbols": len(current_symbols),
            }
        )
    return batches


def build_payload(
    draft_rows: list[dict[str, str]],
    english_rows: dict[int, dict[str, str]],
    char_map: set[str],
) -> dict[str, object]:
    symbols = used_symbols(draft_rows)
    active = active_rows(draft_rows)
    total_bytes = sum(estimated_length(row["korean_text"]) for row in active)
    original_bytes = sum(
        len(english_rows[int(row["pointer_index"])] ["jp_raw_bytes"].split())
        for row in active
    )
    records_growing = []
    for row in active:
        index = int(row["pointer_index"])
        old_length = len(english_rows[index]["jp_raw_bytes"].split())
        new_length = estimated_length(row["korean_text"])
        if new_length > old_length:
            records_growing.append(
                {
                    "pointer_index": index,
                    "original_length": old_length,
                    "estimated_length": new_length,
                    "growth": new_length - old_length,
                }
            )

    status_counts = Counter(row["translation_status"] for row in draft_rows)
    missing_char_map = sorted(symbols - char_map)
    batches = sequential_batches(draft_rows)
    return {
        "status": "FULL_DRAFT_CAPACITY_BLOCKED",
        "source_policy": "English patch supplies pointer ownership and control structure; Korean wording is a separate semantic draft.",
        "draft": {
            "row_count": len(draft_rows),
            "active_row_count": len(active),
            "excluded_row_count": len(draft_rows) - len(active),
            "status_counts": dict(sorted(status_counts.items())),
            "basis_counts": dict(sorted(Counter(row["basis"] for row in draft_rows).items())),
        },
        "font_capacity": {
            "proven_source_code_range": "0x81-0x9A plus 0xC0-0xC7 (opening p182)",
            "proven_source_code_count": len(PROVEN_SOURCE_CODES),
            "unique_non_space_symbols": len(symbols),
            "capacity_gap": max(0, len(symbols) - len(PROVEN_SOURCE_CODES)),
            "font_char_map_count": len(char_map),
            "missing_from_static_char_map": len(missing_char_map),
            "missing_static_characters": missing_char_map,
            "note": "The current Windows-font renderer can draw more glyphs, but the single proven dialogue source pool cannot address them all at once.",
        },
        "space_estimate": {
            "pointer_record_start": f"0x{POINTER_RECORD_START:05X}",
            "pointer_record_limit": f"0x{POINTER_RECORD_LIMIT:05X}",
            "available_bytes": POINTER_RECORD_LIMIT - POINTER_RECORD_START,
            "estimated_compiled_bytes": total_bytes,
            "original_active_record_bytes": original_bytes,
            "estimated_compiled_end": f"0x{POINTER_RECORD_START + total_bytes:05X}",
            "records_that_grow_in_place": len(records_growing),
            "records_that_grow": records_growing,
            "note": "A relocated full stream fits the broad Bank-1 data window by byte count, subject to protected-region and pointer-ownership checks.",
        },
        "recommended_batches": batches,
        "rows": [
            {
                "pointer_index": int(row["pointer_index"]),
                "translation_status": row["translation_status"],
                "korean_text": row["korean_text"],
                "estimated_length": estimated_length(row["korean_text"]),
                "original_length": len(english_rows[int(row["pointer_index"])] ["jp_raw_bytes"].split()),
            }
            for row in draft_rows
        ],
    }


def write_markdown(path: Path, payload: dict[str, object]) -> None:
    draft = payload["draft"]
    capacity = payload["font_capacity"]
    space = payload["space_estimate"]
    batches = payload["recommended_batches"]
    assert isinstance(draft, dict)
    assert isinstance(capacity, dict)
    assert isinstance(space, dict)
    assert isinstance(batches, list)
    lines = [
        "# Pointer Dialogue Korean Draft Audit",
        "",
        "Status: **FULL_DRAFT_CAPACITY_BLOCKED**",
        "",
        "This report joins the 248-entry English-guided pointer ownership map",
        "with a separate Korean semantic draft. It is a build-planning artifact,",
        "not a release translation approval.",
        "",
        "## Coverage",
        "",
        f"- Draft rows: `{draft['row_count']}`; active translation rows: `{draft['active_row_count']}`; excluded: `{draft['excluded_row_count']}`.",
        f"- Translation statuses: `{draft['status_counts']}`.",
        f"- Basis: `{draft['basis_counts']}`.",
        "",
        "## Capacity Gate",
        "",
        f"- Proven direct dialogue source pool: `{capacity['proven_source_code_range']}` ({capacity['proven_source_code_count']} codes).",
        f"- Draft unique non-space symbols: `{capacity['unique_non_space_symbols']}`.",
        f"- Capacity gap: `{capacity['capacity_gap']}` symbols.",
        f"- Static font map misses `{capacity['missing_from_static_char_map']}` of the draft symbols.",
        "- The full build is blocked until the renderer has a multi-page or scene-local font strategy, or the Korean wording is reduced to a proven pool.",
        "",
        "## Space Estimate",
        "",
        f"- Estimated compiled bytes: `{space['estimated_compiled_bytes']}`; original active record bytes: `{space['original_active_record_bytes']}`.",
        f"- Estimated packed end: `{space['estimated_compiled_end']}` inside the broad Bank-1 window.",
        f"- Records longer than their original in-place span: `{space['records_that_grow_in_place']}`.",
        "- This is a relocation feasibility estimate only. A builder must still check every pointer owner, protected record, and code/data boundary.",
        "",
        "## Suggested Batches",
        "",
        "The batches below are greedy capacity groups using the currently proven 34-code opening pool; they are not automatically approved patch targets.",
        "",
        "| batch | pointer indices | records | unique symbols |",
        "| ---: | --- | ---: | ---: |",
    ]
    for number, batch in enumerate(batches, 1):
        indices = batch["pointer_indices"]
        assert isinstance(indices, list)
        lines.append(
            f"| {number} | `{indices[0]}-{indices[-1]}` | {batch['record_count']} | {batch['unique_symbols']} |"
        )
    lines += [
        "",
        "The next compiler may consume one of these batches only after its Korean wording, control bytes, renderer family, and bounded runtime target are declared.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--english", type=Path, default=DEFAULT_ENGLISH)
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    draft = validate_draft(load_tsv(args.draft))
    english = english_pointer_rows(load_tsv(args.english))
    char_map = set(json.loads(args.char_map.read_text(encoding="utf-8"))["sorted"])
    payload = build_payload(draft, english, char_map)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(args.output_markdown, payload)
    print(f"draft_rows={payload['draft']['row_count']}")
    print(f"unique_symbols={payload['font_capacity']['unique_non_space_symbols']}")
    print(f"capacity_gap={payload['font_capacity']['capacity_gap']}")
    print(f"estimated_compiled_bytes={payload['space_estimate']['estimated_compiled_bytes']}")
    print(f"recommended_batches={len(payload['recommended_batches'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

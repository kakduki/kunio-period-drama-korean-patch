#!/usr/bin/env python3
"""Build the complete Bank 1 pointer-dialogue worklist.

The English patch is used here as a structural index only. English wording is
kept as a reference for ordering and record boundaries; it is not copied into
the Korean build. The output deliberately leaves Korean translation blank
until the Japanese record has a renderer and screen context.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from rom_utils import REPO_ROOT


POINTER_COUNT = 248
POINTER_TABLE_START = 0x05DD4
POINTER_TABLE_END = POINTER_TABLE_START + POINTER_COUNT * 2
DEFAULT_ENGLISH_DUMP = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_CONSERVATIVE_CATALOG = REPO_ROOT / "text_data" / "script_catalog.tsv"
DEFAULT_OUTPUT_TSV = REPO_ROOT / "rom_analysis" / "pointer_dialogue_catalog.tsv"
DEFAULT_OUTPUT_JSON = REPO_ROOT / "rom_analysis" / "pointer_dialogue_catalog.json"
DEFAULT_OUTPUT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pointer_dialogue_catalog.md"


OUTPUT_COLUMNS = (
    "id",
    "pointer_index",
    "pointer_rom_offset",
    "prg_bank",
    "jp_pointer_cpu",
    "en_pointer_cpu",
    "jp_rom_offset",
    "en_rom_offset",
    "jp_length",
    "en_length",
    "jp_bytes",
    "en_bytes",
    "english_reference",
    "target_scope",
    "english_pointer_changed",
    "conservative_catalog_status",
    "korean_work_status",
    "screen_context",
    "route_requirement",
    "notes",
)


def hex_value(value: str) -> int:
    return int(value, 16) if value.lower().startswith("0x") else int(value, 16)


def byte_count(value: str) -> int:
    return len(value.split()) if value.strip() else 0


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate_english_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    pointer_rows = [row for row in rows if row.get("record_kind") == "pointer_pair"]
    if len(pointer_rows) != POINTER_COUNT:
        raise ValueError(
            f"expected {POINTER_COUNT} pointer rows, found {len(pointer_rows)}"
        )
    indices = [int(row["pointer_index"]) for row in pointer_rows]
    if indices != list(range(POINTER_COUNT)):
        raise ValueError("pointer rows are not a complete ordered 0..247 sequence")
    for row in pointer_rows:
        index = int(row["pointer_index"])
        expected_offset = POINTER_TABLE_START + index * 2
        if hex_value(row["pointer_rom_offset"]) != expected_offset:
            raise ValueError(f"{row['record_id']} has an unexpected pointer offset")
    return pointer_rows


def status_for(index: int, conservative: dict[str, str] | None) -> tuple[str, str, str, str]:
    if 182 <= index <= 195:
        return (
            "development_verified_opening",
            "opening dialogue",
            "bounded opening route; no combat required",
            "Fourteen opening records have bounded source/PPU evidence and development candidates. This is not release translation approval.",
        )
    if conservative is not None:
        return (
            "structural_unknown",
            "unresolved pointer-dialogue context",
            "named route, save state, or cheat state required",
            "Present in the conservative catalog, but Japanese dialogue glyph mapping and screen context are incomplete.",
        )
    return (
        "structural_unknown_missing_conservative_row",
        "unresolved pointer-dialogue context",
        "named route, save state, or cheat state required",
        "Present in the complete English-guided pointer map but absent from the conservative catalog; investigate before translation.",
    )


def build_rows(
    english_rows: list[dict[str, str]], conservative_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    conservative = {row["id"]: row for row in conservative_rows if row.get("id")}
    output: list[dict[str, str]] = []
    for row in validate_english_rows(english_rows):
        index = int(row["pointer_index"])
        catalog_row = conservative.get(f"PTR-{index:03d}")
        work_status, context, route, notes = status_for(index, catalog_row)
        jp_pointer = hex_value(row["jp_pointer_cpu"])
        en_pointer = hex_value(row["en_pointer_cpu"])
        output.append(
            {
                "id": row["record_id"],
                "pointer_index": str(index),
                "pointer_rom_offset": row["pointer_rom_offset"],
                "prg_bank": "1",
                "jp_pointer_cpu": row["jp_pointer_cpu"],
                "en_pointer_cpu": row["en_pointer_cpu"],
                "jp_rom_offset": row["jp_rom_offset"],
                "en_rom_offset": row["en_rom_offset"],
                "jp_length": str(byte_count(row["jp_raw_bytes"])),
                "en_length": str(byte_count(row["en_raw_bytes"])),
                "jp_bytes": row["jp_raw_bytes"],
                "en_bytes": row["en_raw_bytes"],
                "english_reference": row["en_text"],
                "target_scope": row["target_scope"],
                "english_pointer_changed": str(jp_pointer != en_pointer).lower(),
                "conservative_catalog_status": (
                    catalog_row.get("status", "") if catalog_row else "missing"
                ),
                "korean_work_status": work_status,
                "screen_context": context,
                "route_requirement": route,
                "notes": notes,
            }
        )
    return output


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def report_payload(rows: list[dict[str, str]]) -> dict[str, object]:
    counts = Counter(row["korean_work_status"] for row in rows)
    missing = [row["id"] for row in rows if row["conservative_catalog_status"] == "missing"]
    return {
        "pointer_table": {
            "rom_start": f"0x{POINTER_TABLE_START:05X}",
            "rom_end_exclusive": f"0x{POINTER_TABLE_END:05X}",
            "count": len(rows),
            "prg_bank": 1,
        },
        "source_policy": "English patch supplies structure only; Japanese ROM and contextual transcription supply meaning.",
        "status_counts": dict(sorted(counts.items())),
        "missing_conservative_rows": missing,
        "verified_development_rows": [
            row["id"] for row in rows if row["korean_work_status"] == "development_verified_opening"
        ],
        "rows": rows,
    }


def write_reports(
    json_path: Path, markdown_path: Path, payload: dict[str, object]
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = payload["status_counts"]
    assert isinstance(counts, dict)
    missing = payload["missing_conservative_rows"]
    assert isinstance(missing, list)
    verified = payload["verified_development_rows"]
    assert isinstance(verified, list)
    lines = [
        "# Complete Pointer Dialogue Catalog",
        "",
        "This catalog is the structural starting point for the Korean patch.",
        "The English patch supplies record order, pointer ownership, and a",
        "reference rendering path only. Its wording is not Korean translation.",
        "",
        "## Coverage",
        "",
        f"- Pointer table: `0x{POINTER_TABLE_START:05X}-0x{POINTER_TABLE_END - 1:05X}`",
        f"- Records: `{len(payload['rows'])}` / `{POINTER_COUNT}`",
        f"- Development-verified opening rows: `{', '.join(verified)}`",
        f"- Rows absent from the conservative catalog: `{', '.join(missing) or 'none'}`",
        "",
        "| Korean work status | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(counts.items()):
        lines.append(f"| `{key}` | {value} |")
    lines += [
        "",
        "## Per-record contract",
        "",
        "A row cannot enter a Korean candidate until it has a Japanese meaning,",
        "renderer family, screen context, route, explicit controls, font slots,",
        "and a bounded capture result. Unknown rows remain worklist entries.",
        "",
        "| ID | JP offset | EN reference | JP bytes | Korean work status | Route |",
        "| --- | ---: | --- | ---: | --- | --- |",
    ]
    rows = payload["rows"]
    assert isinstance(rows, list)
    for row in rows:
        lines.append(
            f"| `{row['id']}` | `{row['jp_rom_offset']}` | {row['english_reference']} | "
            f"{row['jp_length']} | `{row['korean_work_status']}` | {row['route_requirement']} |"
        )
    lines += [
        "",
        "The TSV and JSON files preserve all original and reference bytes so a",
        "future compiler can build a declared record without rediscovering it by",
        "blind autoplay.",
        "",
    ]
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english-dump", type=Path, default=DEFAULT_ENGLISH_DUMP)
    parser.add_argument("--conservative-catalog", type=Path, default=DEFAULT_CONSERVATIVE_CATALOG)
    parser.add_argument("--output-tsv", type=Path, default=DEFAULT_OUTPUT_TSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    args = parser.parse_args()
    rows = build_rows(load_rows(args.english_dump), load_rows(args.conservative_catalog))
    write_tsv(args.output_tsv, rows)
    payload = report_payload(rows)
    write_reports(args.output_json, args.output_markdown, payload)
    print(f"pointer_rows={len(rows)}")
    print(f"missing_conservative_rows={','.join(payload['missing_conservative_rows']) or 'none'}")
    print(f"tsv={args.output_tsv}")
    print(f"json={args.output_json}")
    print(f"markdown={args.output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a structural text map from a reference English IPS in memory.

The reference IPS is used only as an analysis input. This tool never writes a
patched ROM and does not copy the IPS into the repository.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from analyze_reference_ips import (
    IpsRecord,
    apply_records,
    parse_ines_layout,
    parse_ips,
    region_for_offset,
)
from rom_utils import REPO_ROOT


DEFAULT_ANALYSIS_DIR = REPO_ROOT / "rom_analysis"
DEFAULT_TEXT_DIR = REPO_ROOT / "text_data"

BANK1_INDEX = 1
BANK_SIZE = 0x4000
CPU_BANK_START = 0x8000
CPU_BANK_END = 0xC000

NAME_TABLE_START = 0x0561B
PREPOINTER_TEXT_START = 0x056BC
POINTER_TABLE_START = 0x05DD4
EXPECTED_POINTER_TABLE_END = 0x05FC4
EXPECTED_POINTER_COUNT = 248

REFERENCE_RANGES = (
    ("renderer_support", 0x05288, 0x052C7, "medium"),
    ("name_table", NAME_TABLE_START, PREPOINTER_TEXT_START, "medium"),
    ("prepointer_text", PREPOINTER_TEXT_START, POINTER_TABLE_START, "medium"),
    (
        "dialogue_pointer_table",
        POINTER_TABLE_START,
        EXPECTED_POINTER_TABLE_END,
        "high",
    ),
    ("pointer_driven_text", EXPECTED_POINTER_TABLE_END, 0x07767, "high"),
    ("growth_ui", 0x07894, 0x078AB, "medium"),
    ("menu_or_label", 0x07FB6, 0x07FED, "medium"),
    ("menu_or_label", 0x07FF7, 0x0800F, "medium"),
)

RECORD_MAP_COLUMNS = (
    "record_index",
    "rom_offset",
    "end_exclusive",
    "length",
    "region",
    "prg_bank",
    "rle",
    "final_changed_bytes",
    "classification",
    "confidence",
)

SCRIPT_DUMP_COLUMNS = (
    "record_id",
    "record_kind",
    "source_language",
    "context",
    "pointer_index",
    "pointer_rom_offset",
    "jp_pointer_cpu",
    "en_pointer_cpu",
    "jp_rom_offset",
    "en_rom_offset",
    "jp_window_end",
    "en_window_end",
    "jp_first_ff_end",
    "en_first_ff_end",
    "jp_raw_bytes",
    "en_raw_bytes",
    "jp_text",
    "en_text",
    "target_scope",
    "target_references",
    "structural_confidence",
    "notes",
)

CATALOG_COLUMNS = (
    "id",
    "context",
    "jp_offset",
    "jp_text",
    "en_offset",
    "en_text",
    "pointer_offset",
    "terminator",
    "max_width",
    "status",
    "confidence",
    "notes",
)


@dataclass(frozen=True)
class PointerEntry:
    index: int
    table_rom_offset: int
    cpu_address: int
    target_rom_offset: int
    target_in_bank: bool


@dataclass(frozen=True)
class DelimitedRecord:
    index: int
    start: int
    end_exclusive: int
    has_ff_delimiter: bool
    data: bytes


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def hex_offset(value: int | None) -> str:
    return "" if value is None else f"0x{value:05X}"


def hex_cpu(value: int | None) -> str:
    return "" if value is None else f"0x{value:04X}"


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{value:02X}" for value in data)


def spans_overlap(
    left_start: int, left_end: int, right_start: int, right_end: int
) -> bool:
    return left_start < right_end and right_start < left_end


def bank1_bounds(rom: bytes) -> tuple[int, int]:
    layout = parse_ines_layout(rom)
    start = layout.prg_start + BANK1_INDEX * BANK_SIZE
    end = start + BANK_SIZE
    if end > layout.prg_end:
        raise ValueError("reference layout does not contain PRG bank 1")
    return start, end


def find_base_rom_path(candidate: str | None) -> Path:
    """Resolve the base ROM without treating another option's value as a ROM."""

    if candidate:
        path = Path(candidate).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(f"base ROM not found: {path}")
    roms = sorted((REPO_ROOT / "rom").glob("*.nes"))
    if roms:
        return roms[0]
    raise FileNotFoundError(
        "base ROM not found. Put a .nes file in rom/ or pass it as the first argument."
    )


def parse_pointer_table(
    data: bytes, start: int, bank_start: int, bank_end: int
) -> tuple[list[PointerEntry], int]:
    """Read consecutive CPU-bank pointers until the first non-pointer word."""

    entries: list[PointerEntry] = []
    offset = start
    while offset + 2 <= len(data):
        cpu_address = int.from_bytes(data[offset : offset + 2], "little")
        if not CPU_BANK_START <= cpu_address < CPU_BANK_END:
            break
        target = bank_start + (cpu_address - CPU_BANK_START)
        entries.append(
            PointerEntry(
                index=len(entries),
                table_rom_offset=offset,
                cpu_address=cpu_address,
                target_rom_offset=target,
                target_in_bank=bank_start <= target < bank_end,
            )
        )
        offset += 2
    return entries, offset


def parse_fixed_pointer_table(
    data: bytes, start: int, count: int, bank_start: int, bank_end: int
) -> list[PointerEntry]:
    entries: list[PointerEntry] = []
    end = start + count * 2
    if end > len(data):
        raise ValueError("pointer table extends past the ROM")
    for index, offset in enumerate(range(start, end, 2)):
        cpu_address = int.from_bytes(data[offset : offset + 2], "little")
        if not CPU_BANK_START <= cpu_address < CPU_BANK_END:
            raise ValueError(
                f"base pointer {index} at 0x{offset:05X} is outside $8000-$BFFF"
            )
        target = bank_start + (cpu_address - CPU_BANK_START)
        entries.append(
            PointerEntry(
                index=index,
                table_rom_offset=offset,
                cpu_address=cpu_address,
                target_rom_offset=target,
                target_in_bank=bank_start <= target < bank_end,
            )
        )
    return entries


def validate_reference_pointer_table(
    entries: list[PointerEntry], end_exclusive: int
) -> None:
    if end_exclusive != EXPECTED_POINTER_TABLE_END:
        raise ValueError(
            "unexpected English pointer-table boundary: "
            f"0x{end_exclusive:05X}, expected 0x{EXPECTED_POINTER_TABLE_END:05X}"
        )
    if len(entries) != EXPECTED_POINTER_COUNT:
        raise ValueError(
            "unexpected English pointer count: "
            f"{len(entries)}, expected {EXPECTED_POINTER_COUNT}"
        )


def split_ff_records(data: bytes, start: int, end: int) -> list[DelimitedRecord]:
    """Split a block into byte-preserving records ending at 0xFF when present."""

    records: list[DelimitedRecord] = []
    cursor = start
    for offset in range(start, end):
        if data[offset] != 0xFF:
            continue
        records.append(
            DelimitedRecord(
                index=len(records),
                start=cursor,
                end_exclusive=offset + 1,
                has_ff_delimiter=True,
                data=data[cursor : offset + 1],
            )
        )
        cursor = offset + 1
    if cursor < end:
        records.append(
            DelimitedRecord(
                index=len(records),
                start=cursor,
                end_exclusive=end,
                has_ff_delimiter=False,
                data=data[cursor:end],
            )
        )
    return records


def decode_english_dialogue(data: bytes) -> str:
    """Decode only the verified English glyph path; preserve all controls."""

    output: list[str] = []
    for value in data:
        if value == 0x80:
            output.append(" ")
        elif 0x81 <= value <= 0x9A:
            output.append(chr(ord("A") + value - 0x81))
        else:
            output.append(f"<{value:02X}>")
    return "".join(output)


def decode_japanese_dialogue(data: bytes) -> str:
    """Preserve original dialogue bytes until its separate tile path is mapped."""

    return "".join(f"<{value:02X}>" for value in data)


def target_windows(
    entries: Iterable[PointerEntry], data_start: int, data_end: int
) -> dict[int, int | None]:
    targets = sorted(
        {
            entry.target_rom_offset
            for entry in entries
            if data_start <= entry.target_rom_offset < data_end
        }
    )
    windows: dict[int, int | None] = {}
    for index, target in enumerate(targets):
        windows[target] = targets[index + 1] if index + 1 < len(targets) else data_end
    return windows


def first_ff_end(data: bytes, start: int, end: int | None) -> int | None:
    if end is None or not start <= end <= len(data):
        return None
    found = data.find(b"\xff", start, end)
    return found + 1 if found != -1 else None


def excerpt_end(data: bytes, start: int, window_end: int | None) -> int | None:
    """Prefer a delimiter-bounded excerpt and preserve a shared leading 0xFF."""

    first_end = first_ff_end(data, start, window_end)
    if first_end is None:
        return window_end
    if first_end != start + 1:
        return first_end
    second_end = first_ff_end(data, first_end, window_end)
    return second_end or first_end


def target_scope(target: int, table_start: int, data_start: int, bank_end: int) -> str:
    bank_start = bank_end - BANK_SIZE
    if not bank_start <= target < bank_end:
        return "outside_bank1"
    if target < table_start:
        return "bank1_before_pointer_table"
    if target < data_start:
        return "pointer_table"
    return "bank1_after_pointer_table"


def count_english_letters(data: bytes) -> int:
    return sum(0x81 <= value <= 0x9A for value in data)


def count_japanese_payload_bytes(data: bytes) -> int:
    return sum(value not in {0x00, 0xFF} for value in data)


def make_pointer_rows(
    base: bytes,
    english: bytes,
    jp_entries: list[PointerEntry],
    en_entries: list[PointerEntry],
    table_end: int,
    bank_end: int,
) -> list[dict[str, object]]:
    if len(jp_entries) != len(en_entries):
        raise ValueError("Japanese and English pointer tables have different lengths")

    jp_windows = target_windows(jp_entries, table_end, bank_end)
    en_windows = target_windows(en_entries, table_end, bank_end)
    en_target_counts = Counter(entry.target_rom_offset for entry in en_entries)
    rows: list[dict[str, object]] = []

    for jp_entry, en_entry in zip(jp_entries, en_entries, strict=True):
        jp_window_end = jp_windows.get(jp_entry.target_rom_offset)
        en_window_end = en_windows.get(en_entry.target_rom_offset)
        jp_excerpt_end = excerpt_end(base, jp_entry.target_rom_offset, jp_window_end)
        en_excerpt_end = excerpt_end(english, en_entry.target_rom_offset, en_window_end)
        jp_data = (
            base[jp_entry.target_rom_offset : jp_excerpt_end]
            if jp_excerpt_end is not None
            else b""
        )
        en_data = (
            english[en_entry.target_rom_offset : en_excerpt_end]
            if en_excerpt_end is not None
            else b""
        )
        scope = target_scope(
            en_entry.target_rom_offset,
            POINTER_TABLE_START,
            table_end,
            bank_end,
        )
        notes: list[str] = []
        if en_target_counts[en_entry.target_rom_offset] > 1:
            notes.append("duplicate English target")
        if en_window_end is None:
            notes.append("target outside pointer-driven storage")
        if en_excerpt_end == en_entry.target_rom_offset + 1:
            notes.append("shared leading 0xFF or empty record")
        rows.append(
            {
                "record_id": f"PTR-{en_entry.index:03d}",
                "record_kind": "pointer_pair",
                "source_language": "paired",
                "context": "Bank 1 pointer-driven text",
                "pointer_index": en_entry.index,
                "pointer_rom_offset": hex_offset(en_entry.table_rom_offset),
                "jp_pointer_cpu": hex_cpu(jp_entry.cpu_address),
                "en_pointer_cpu": hex_cpu(en_entry.cpu_address),
                "jp_rom_offset": hex_offset(jp_entry.target_rom_offset),
                "en_rom_offset": hex_offset(en_entry.target_rom_offset),
                "jp_window_end": hex_offset(jp_window_end),
                "en_window_end": hex_offset(en_window_end),
                "jp_first_ff_end": hex_offset(
                    first_ff_end(base, jp_entry.target_rom_offset, jp_window_end)
                ),
                "en_first_ff_end": hex_offset(
                    first_ff_end(english, en_entry.target_rom_offset, en_window_end)
                ),
                "jp_raw_bytes": hex_bytes(jp_data),
                "en_raw_bytes": hex_bytes(en_data),
                "jp_text": decode_japanese_dialogue(jp_data),
                "en_text": decode_english_dialogue(en_data),
                "target_scope": scope,
                "target_references": en_target_counts[en_entry.target_rom_offset],
                "structural_confidence": (
                    "high"
                    if scope == "bank1_after_pointer_table"
                    else "medium"
                ),
                "notes": "; ".join(notes) or "none",
                "_jp_data": jp_data,
                "_en_data": en_data,
            }
        )
    return rows


def make_delimited_rows(
    data: bytes,
    *,
    language: str,
    start: int,
    end: int,
    context: str,
    id_prefix: str,
) -> list[dict[str, object]]:
    decode = (
        decode_english_dialogue if language == "english" else decode_japanese_dialogue
    )
    rows: list[dict[str, object]] = []
    for record in split_ff_records(data, start, end):
        is_english = language == "english"
        rows.append(
            {
                "record_id": f"{id_prefix}-{record.index:03d}",
                "record_kind": "ff_delimited",
                "source_language": language,
                "context": context,
                "pointer_index": "",
                "pointer_rom_offset": "",
                "jp_pointer_cpu": "",
                "en_pointer_cpu": "",
                "jp_rom_offset": hex_offset(record.start) if not is_english else "",
                "en_rom_offset": hex_offset(record.start) if is_english else "",
                "jp_window_end": hex_offset(record.end_exclusive) if not is_english else "",
                "en_window_end": hex_offset(record.end_exclusive) if is_english else "",
                "jp_first_ff_end": (
                    hex_offset(record.end_exclusive)
                    if not is_english and record.has_ff_delimiter
                    else ""
                ),
                "en_first_ff_end": (
                    hex_offset(record.end_exclusive)
                    if is_english and record.has_ff_delimiter
                    else ""
                ),
                "jp_raw_bytes": hex_bytes(record.data) if not is_english else "",
                "en_raw_bytes": hex_bytes(record.data) if is_english else "",
                "jp_text": decode(record.data) if not is_english else "",
                "en_text": decode(record.data) if is_english else "",
                "target_scope": "pre-pointer block",
                "target_references": "",
                "structural_confidence": "medium",
                "notes": (
                    "0xFF-delimited record; not paired because translated lengths differ"
                    if record.has_ff_delimiter
                    else "unterminated tail record; not paired"
                ),
            }
        )
    return rows


def classify_record(record: IpsRecord, layout_end: int) -> tuple[str, str]:
    start = record.offset
    end = start + len(record.data)
    if start < 16:
        return "header", "high"
    if start >= layout_end:
        return "trailing", "low"

    classifications: list[str] = []
    confidence_rank = {"low": 0, "medium": 1, "high": 2}
    confidence = "low"
    for label, range_start, range_end, range_confidence in REFERENCE_RANGES:
        if spans_overlap(start, end, range_start, range_end):
            classifications.append(label)
            if confidence_rank[range_confidence] > confidence_rank[confidence]:
                confidence = range_confidence
    if classifications:
        return "+".join(dict.fromkeys(classifications)), confidence
    return "other_prg", "low"


def make_record_map(
    base: bytes, english: bytes, records: list[IpsRecord]
) -> list[dict[str, object]]:
    layout = parse_ines_layout(base)
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        start = record.offset
        end = start + len(record.data)
        region, bank = region_for_offset(start, layout)
        if region == "CHR":
            classification, confidence = "font_or_tiles", "high"
        elif region == "header":
            classification, confidence = "header", "high"
        else:
            classification, confidence = classify_record(record, layout.prg_end)
        changed = sum(
            offset >= len(base) or base[offset] != english[offset]
            for offset in range(start, min(end, len(english)))
        )
        rows.append(
            {
                "record_index": index,
                "rom_offset": hex_offset(start),
                "end_exclusive": hex_offset(end),
                "length": len(record.data),
                "region": region,
                "prg_bank": "" if bank is None else bank,
                "rle": record.rle,
                "final_changed_bytes": changed,
                "classification": classification,
                "confidence": confidence,
            }
        )
    return rows


def catalog_rows(pointer_rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for pointer in pointer_rows:
        jp_data = pointer["_jp_data"]
        en_data = pointer["_en_data"]
        if pointer["target_scope"] != "bank1_after_pointer_table":
            continue
        if count_english_letters(en_data) < 3 or count_japanese_payload_bytes(jp_data) < 2:
            continue
        rows.append(
            {
                "id": pointer["record_id"],
                "context": pointer["context"],
                "jp_offset": pointer["jp_rom_offset"],
                "jp_text": pointer["jp_text"],
                "en_offset": pointer["en_rom_offset"],
                "en_text": pointer["en_text"],
                "pointer_offset": pointer["pointer_rom_offset"],
                "terminator": (
                    pointer["en_first_ff_end"] or "no 0xFF before next target"
                ),
                "max_width": "UNKNOWN",
                "status": "needs_japanese_dialogue_glyph_map",
                "confidence": "structural-high; Japanese glyph map pending",
                "notes": (
                    "Pointer index is paired across base/reference. "
                    "Japanese bytes remain tokenized until the dialogue tile path is mapped."
                ),
            }
        )
    return rows


def write_csv(path: Path, columns: Iterable[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_tsv(path: Path, columns: Iterable[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(columns),
            delimiter="\t",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def pointer_payload(
    base: bytes,
    english: bytes,
    table_end: int,
    jp_entries: list[PointerEntry],
    en_entries: list[PointerEntry],
) -> dict[str, object]:
    return {
        "source": {
            "base_md5": md5(base),
            "base_sha256": sha256(base),
            "reference_ips_not_stored": True,
        },
        "pointer_table": {
            "bank_index": BANK1_INDEX,
            "rom_start": hex_offset(POINTER_TABLE_START),
            "rom_end_exclusive": hex_offset(table_end),
            "entry_count": len(en_entries),
            "cpu_range": "$8000-$BFFF",
            "first_non_pointer_word": (
                f"0x{int.from_bytes(english[table_end:table_end + 2], 'little'):04X}"
            ),
        },
        "entries": [
            {
                "index": en_entry.index,
                "pointer_rom_offset": hex_offset(en_entry.table_rom_offset),
                "jp_pointer_cpu": hex_cpu(jp_entry.cpu_address),
                "en_pointer_cpu": hex_cpu(en_entry.cpu_address),
                "jp_target_rom_offset": hex_offset(jp_entry.target_rom_offset),
                "en_target_rom_offset": hex_offset(en_entry.target_rom_offset),
                "pointer_changed": jp_entry.cpu_address != en_entry.cpu_address,
                "en_target_in_bank1": en_entry.target_in_bank,
            }
            for jp_entry, en_entry in zip(jp_entries, en_entries, strict=True)
        ],
    }


def render_notes(
    *,
    ips_path: Path,
    table_end: int,
    pointer_rows: list[dict[str, object]],
    catalog: list[dict[str, object]],
) -> str:
    after_table = sum(
        row["target_scope"] == "bank1_after_pointer_table" for row in pointer_rows
    )
    changed_pointers = sum(
        row["jp_pointer_cpu"] != row["en_pointer_cpu"] for row in pointer_rows
    )
    return "\n".join(
        (
            "# English Reference Script Map",
            "",
            "Generated by scripts/extract_english_reference_script.py.",
            "The third-party IPS is an input only; neither it nor a patched ROM is stored.",
            "",
            "## Verified Structure",
            "",
            f"- English reference IPS: {ips_path.name}",
            f"- Pointer table: 0x{POINTER_TABLE_START:05X}-0x{table_end - 1:05X}",
            f"- Pointer count: {len(pointer_rows)}",
            f"- Pointer entries changed by the English patch: {changed_pointers}",
            f"- Entries targeting Bank 1 data after the table: {after_table}",
            f"- Conservative paired rows in text_data/script_catalog.tsv: {len(catalog)}",
            "",
            "## Interpretation Rules",
            "",
            "- A paired pointer index proves structural correspondence, not screen context.",
            "- 0x81-0x9A is decoded as English A-Z; 0x80 is the observed English space tile.",
            "- The Japanese preview keeps every byte as an <XX> token until the original dialogue-tile path is mapped.",
            "- 0xFF is recorded as a delimiter/control boundary, not assumed to be a universal string terminator.",
            "- Pre-pointer records are emitted per language but deliberately not paired by ordinal index, because translated lengths change record boundaries.",
            "",
            "Use this map before making a Korean candidate ROM. Do not revive opening-screen autoplay to discover these records.",
            "",
        )
    )


def build_outputs(base: bytes, ips: bytes, ips_path: Path) -> dict[str, object]:
    records, truncate_size = parse_ips(ips)
    if truncate_size is not None:
        raise ValueError("the reference IPS unexpectedly uses a truncate footer")
    english = apply_records(base, records, truncate_size)
    bank_start, bank_end = bank1_bounds(base)
    en_entries, table_end = parse_pointer_table(
        english, POINTER_TABLE_START, bank_start, bank_end
    )
    validate_reference_pointer_table(en_entries, table_end)
    jp_entries = parse_fixed_pointer_table(
        base,
        POINTER_TABLE_START,
        len(en_entries),
        bank_start,
        bank_end,
    )

    pointer_rows = make_pointer_rows(
        base,
        english,
        jp_entries,
        en_entries,
        table_end,
        bank_end,
    )
    dump_rows = [
        *make_delimited_rows(
            base,
            language="japanese",
            start=NAME_TABLE_START,
            end=PREPOINTER_TEXT_START,
            context="Bank 1 name-table area",
            id_prefix="JP-NAME",
        ),
        *make_delimited_rows(
            english,
            language="english",
            start=NAME_TABLE_START,
            end=PREPOINTER_TEXT_START,
            context="Bank 1 name-table area",
            id_prefix="EN-NAME",
        ),
        *make_delimited_rows(
            base,
            language="japanese",
            start=PREPOINTER_TEXT_START,
            end=POINTER_TABLE_START,
            context="Bank 1 pre-pointer text area",
            id_prefix="JP-PRE",
        ),
        *make_delimited_rows(
            english,
            language="english",
            start=PREPOINTER_TEXT_START,
            end=POINTER_TABLE_START,
            context="Bank 1 pre-pointer text area",
            id_prefix="EN-PRE",
        ),
        *pointer_rows,
    ]
    catalog = catalog_rows(pointer_rows)
    return {
        "records": records,
        "english": english,
        "pointer_table_end": table_end,
        "jp_entries": jp_entries,
        "en_entries": en_entries,
        "pointer_rows": pointer_rows,
        "dump_rows": dump_rows,
        "catalog": catalog,
        "record_map": make_record_map(base, english, records),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "rom",
        nargs="?",
        help="Base Japanese ROM; defaults to the first rom/*.nes file.",
    )
    parser.add_argument(
        "--reference-ips",
        required=True,
        type=Path,
        help="Path to the English reference IPS. It is read but never copied.",
    )
    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_DIR,
        help="Directory for analysis CSV, JSON, and Markdown output.",
    )
    parser.add_argument(
        "--text-dir",
        type=Path,
        default=DEFAULT_TEXT_DIR,
        help="Directory for the conservative script catalog TSV.",
    )
    args = parser.parse_args()

    rom_path = find_base_rom_path(args.rom)
    ips_path = args.reference_ips.expanduser()
    if not ips_path.is_file():
        raise FileNotFoundError(f"reference IPS not found: {ips_path}")

    base = rom_path.read_bytes()
    outputs = build_outputs(base, ips_path.read_bytes(), ips_path)
    analysis_dir = args.analysis_dir
    text_dir = args.text_dir

    write_csv(
        analysis_dir / "english_patch_record_map.csv",
        RECORD_MAP_COLUMNS,
        outputs["record_map"],
    )
    write_tsv(
        analysis_dir / "english_script_dump.tsv",
        SCRIPT_DUMP_COLUMNS,
        outputs["dump_rows"],
    )
    (analysis_dir / "english_pointer_map.json").write_text(
        json.dumps(
            pointer_payload(
                base,
                outputs["english"],
                outputs["pointer_table_end"],
                outputs["jp_entries"],
                outputs["en_entries"],
            ),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_tsv(text_dir / "script_catalog.tsv", CATALOG_COLUMNS, outputs["catalog"])
    (analysis_dir / "english_script_reference.md").write_text(
        render_notes(
            ips_path=ips_path,
            table_end=outputs["pointer_table_end"],
            pointer_rows=outputs["pointer_rows"],
            catalog=outputs["catalog"],
        ),
        encoding="utf-8",
    )

    print(f"record_map={analysis_dir / 'english_patch_record_map.csv'}")
    print(f"script_dump={analysis_dir / 'english_script_dump.tsv'}")
    print(f"pointer_map={analysis_dir / 'english_pointer_map.json'}")
    print(f"catalog={text_dir / 'script_catalog.tsv'}")
    print(f"pointer_count={len(outputs['en_entries'])}")
    print(f"catalog_rows={len(outputs['catalog'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

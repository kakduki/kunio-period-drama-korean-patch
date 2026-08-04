#!/usr/bin/env python3
"""Validate translation rows against the Japanese ROM's known pointer table.

This is a static gate. A row can pass address and glyph checks while its
overall status remains UNKNOWN until a bounded emulator source-read proves
that the record is displayed in the intended scene.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from korean_tile_font import HANDCRAFTED_BITMAPS  # noqa: E402


POINTER_TABLE_OFFSET = 0x05DD4
POINTER_COUNT = 248
CPU_WINDOW_START = 0x8000
FILE_WINDOW_START = 0x4010
MAX_RECORD_SCAN = 0x200
REQUIRED_COLUMNS = {
    "id",
    "translated_text",
    "pointer_address",
    "max_bytes",
}


def parse_int(value: str) -> int | None:
    try:
        return int(value.strip(), 0)
    except (AttributeError, ValueError):
        return None


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def pointer_target(rom: bytes, pointer_address: int) -> tuple[int, int] | None:
    delta = pointer_address - POINTER_TABLE_OFFSET
    if delta < 0 or delta % 2:
        return None
    index = delta // 2
    if index >= POINTER_COUNT:
        return None
    pointer = int.from_bytes(rom[pointer_address : pointer_address + 2], "little")
    target = FILE_WINDOW_START + (pointer - CPU_WINDOW_START)
    if target < 0 or target >= len(rom):
        return None
    return index, target


def record_bytes(rom: bytes, target: int) -> tuple[bytes, str]:
    end = min(len(rom), target + MAX_RECORD_SCAN)
    payload = rom[target:end]
    terminator = payload.find(b"\xFF")
    if terminator >= 0:
        return payload[: terminator + 1], "HEURISTIC_FIRST_FF"
    return payload, f"UNTERMINATED_WITHIN_0x{MAX_RECORD_SCAN:X}"


def row_result(row: dict[str, str], rom: bytes, seen_ids: set[str], seen_pointers: set[int]) -> dict[str, object]:
    row_id = (row.get("id") or "UNKNOWN").strip() or "UNKNOWN"
    translated = (row.get("translated_text") or "").strip()
    pointer_text = (row.get("pointer_address") or "").strip()
    max_bytes = parse_int(row.get("max_bytes") or "")
    errors: list[str] = []
    warnings: list[str] = []
    if row_id in seen_ids:
        errors.append("duplicate_id")
    seen_ids.add(row_id)
    if not translated or translated.upper() == "UNKNOWN":
        errors.append("empty_or_unknown_translation")
    if max_bytes is None or max_bytes <= 0:
        errors.append("invalid_max_bytes")

    pointer = parse_int(pointer_text)
    index: int | None = None
    target: int | None = None
    raw = b""
    termination = "UNKNOWN"
    if pointer is None:
        warnings.append("pointer_address_unknown")
    else:
        if pointer in seen_pointers:
            errors.append("duplicate_pointer_address")
        seen_pointers.add(pointer)
        resolved = pointer_target(rom, pointer)
        if resolved is None:
            errors.append("pointer_not_in_declared_table")
        else:
            index, target = resolved
            raw, termination = record_bytes(rom, target)

    missing_glyphs = sorted({character for character in translated if character not in HANDCRAFTED_BITMAPS})
    if missing_glyphs:
        warnings.append("glyphs_not_in_handcrafted_minimum")

    static_status = "FAIL" if errors else "UNKNOWN" if pointer is None else "PASS"
    overall_status = "FAIL" if errors else "UNKNOWN"
    return {
        "id": row_id,
        "category": (row.get("category") or "UNKNOWN").strip() or "UNKNOWN",
        "translated_text": translated,
        "pointer_address": f"0x{pointer:05X}" if pointer is not None else "UNKNOWN",
        "pointer_index": index if index is not None else "UNKNOWN",
        "text_address": f"0x{target:05X}" if target is not None else "UNKNOWN",
        "original_bytes": raw.hex(" ").upper() if raw else "UNKNOWN",
        "termination_status": termination,
        "missing_handcrafted_glyphs": "".join(missing_glyphs) or "NONE",
        "static_status": static_status,
        "status": overall_status,
        "reason": ";".join(errors or ["runtime_source_read_and_visual_gate_pending"]),
        "warnings": ";".join(warnings) or "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=ROOT / "translation" / "script.csv")
    parser.add_argument("--csv-out", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    rom_path = resolve_path(args.rom).resolve()
    manifest_path = resolve_path(args.manifest).resolve()
    csv_path = resolve_path(args.csv_out).resolve()
    json_path = resolve_path(args.json_out).resolve()
    if not rom_path.is_file():
        raise SystemExit(f"ROM not found: {rom_path}")
    if not manifest_path.is_file():
        raise SystemExit(f"manifest not found: {manifest_path}")

    rom = rom_path.read_bytes()
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - columns)
        if missing_columns:
            raise SystemExit(f"manifest missing required columns: {', '.join(missing_columns)}")
        seen_ids: set[str] = set()
        seen_pointers: set[int] = set()
        results = [row_result(row, rom, seen_ids, seen_pointers) for row in reader]

    fieldnames = list(results[0].keys()) if results else ["status"]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    counts = {status: sum(row["status"] == status for row in results) for status in ("PASS", "FAIL", "UNKNOWN")}
    payload = {
        "rom": str(rom_path),
        "manifest": str(manifest_path),
        "pointer_table": {"file_offset": f"0x{POINTER_TABLE_OFFSET:05X}", "count": POINTER_COUNT},
        "rows": results,
        "summary": {"total": len(results), **counts},
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0 if counts["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compile a small Korean dialogue batch with explicit control-byte tokens.

The English patch establishes pointer-table correspondence and font-slot
ownership, but it is not a Korean translation source. This compiler takes a
scene-owned Korean catalog, assigns only verified dialogue glyph slots, and
keeps every non-glyph control byte explicit. It deliberately rejects batches
that exceed the currently verified 17-slot 8x16 dialogue pool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from rom_utils import REPO_ROOT


DEFAULT_CATALOG = REPO_ROOT / "text_data" / "korean_scene_batches" / "opening_ptr_182.json"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "opening_ptr_182_compilation.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_ptr_182_compilation.md"

# `$955F` has renderer-specific branches for these two source codes. Keep the
# allocator out of them until those branches have their own proof.
RESERVED_GLYPH_CODES = frozenset({0x8A, 0x8B})
AVAILABLE_GLYPH_CODES = tuple(
    code for code in range(0x81, 0x94) if code not in RESERVED_GLYPH_CODES
)


class CatalogError(ValueError):
    """Raised when a scene catalog cannot be safely compiled."""


def parse_hex_byte(value: object) -> int:
    if not isinstance(value, str):
        raise CatalogError(f"control byte must be a string, got {value!r}")
    token = value.strip().upper()
    if token.startswith("0X"):
        token = token[2:]
    if len(token) != 2:
        raise CatalogError(f"control byte must contain exactly two hex digits: {value!r}")
    try:
        parsed = int(token, 16)
    except ValueError as exc:
        raise CatalogError(f"invalid control byte: {value!r}") from exc
    if not 0 <= parsed <= 0xFF:
        raise CatalogError(f"control byte outside 0x00-0xFF: {value!r}")
    return parsed


def parse_hex_bytes(value: object, *, field: str) -> bytes:
    if not isinstance(value, str):
        raise CatalogError(f"{field} must be a space-separated hex string")
    values = [part for part in value.split() if part]
    if not values:
        raise CatalogError(f"{field} is empty")
    return bytes(parse_hex_byte(part) for part in values)


def load_catalog(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Korean scene catalog not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(f"invalid JSON catalog: {path}") from exc
    if not isinstance(payload, dict):
        raise CatalogError("catalog root must be an object")
    if payload.get("schema_version") != 1:
        raise CatalogError("unsupported or missing catalog schema_version")
    if not isinstance(payload.get("batch_id"), str) or not payload["batch_id"]:
        raise CatalogError("catalog batch_id is required")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise CatalogError("catalog must contain at least one record")
    return payload


def token_glyphs(records: list[object]) -> list[str]:
    glyphs: list[str] = []
    seen: set[str] = set()
    for record_index, raw_record in enumerate(records):
        if not isinstance(raw_record, dict):
            raise CatalogError(f"record {record_index} must be an object")
        tokens = raw_record.get("tokens")
        if not isinstance(tokens, list) or not tokens:
            raise CatalogError(f"record {record_index} must contain token objects")
        for token_index, token in enumerate(tokens):
            if not isinstance(token, dict):
                raise CatalogError(f"record {record_index} token {token_index} must be an object")
            has_glyph = "glyph" in token
            has_byte = "byte" in token
            if has_glyph == has_byte:
                raise CatalogError(
                    f"record {record_index} token {token_index} must contain exactly one of glyph or byte"
                )
            if has_glyph:
                glyph = token["glyph"]
                if not isinstance(glyph, str) or len(glyph) != 1:
                    raise CatalogError(
                        f"record {record_index} token {token_index} glyph must be one character"
                    )
                if glyph not in seen:
                    seen.add(glyph)
                    glyphs.append(glyph)
            else:
                parse_hex_byte(token["byte"])
    return glyphs


def allocate_glyph_codes(glyphs: list[str]) -> dict[str, int]:
    if len(glyphs) > len(AVAILABLE_GLYPH_CODES):
        raise CatalogError(
            f"batch needs {len(glyphs)} unique glyphs but the verified pool has "
            f"only {len(AVAILABLE_GLYPH_CODES)} slots"
        )
    return {glyph: AVAILABLE_GLYPH_CODES[index] for index, glyph in enumerate(glyphs)}


def encode_tokens(tokens: object, glyph_codes: dict[str, int]) -> bytes:
    if not isinstance(tokens, list):
        raise CatalogError("tokens must be a list")
    encoded = bytearray()
    for token_index, token in enumerate(tokens):
        if not isinstance(token, dict):
            raise CatalogError(f"token {token_index} must be an object")
        if "glyph" in token and "byte" not in token:
            glyph = token["glyph"]
            if glyph not in glyph_codes:
                raise CatalogError(f"token {token_index} refers to an unallocated glyph: {glyph!r}")
            encoded.append(glyph_codes[glyph])
        elif "byte" in token and "glyph" not in token:
            encoded.append(parse_hex_byte(token["byte"]))
        else:
            raise CatalogError(f"token {token_index} must contain exactly one of glyph or byte")
    return bytes(encoded)


def compile_catalog(path: Path) -> dict[str, object]:
    catalog = load_catalog(path)
    raw_records = catalog["records"]
    assert isinstance(raw_records, list)
    glyphs = token_glyphs(raw_records)
    glyph_codes = allocate_glyph_codes(glyphs)
    records: list[dict[str, object]] = []
    for raw_record in raw_records:
        assert isinstance(raw_record, dict)
        record_id = raw_record.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise CatalogError("record id is required")
        expected_length = raw_record.get("expected_length")
        if not isinstance(expected_length, int) or expected_length <= 0:
            raise CatalogError(f"record {record_id} has invalid expected_length")
        original = parse_hex_bytes(raw_record.get("expected_original_bytes"), field=f"{record_id} expected_original_bytes")
        if len(original) != expected_length:
            raise CatalogError(
                f"record {record_id} expected original length is {len(original)}, not {expected_length}"
            )
        encoded = encode_tokens(raw_record.get("tokens"), glyph_codes)
        if len(encoded) != expected_length:
            raise CatalogError(
                f"record {record_id} compiled length is {len(encoded)}, not {expected_length}"
            )
        if encoded[-1] != 0xFF:
            raise CatalogError(f"record {record_id} must end in explicit 0xFF")
        for field in ("context", "pointer_rom_offset", "record_rom_offset", "korean_text"):
            if not isinstance(raw_record.get(field), str) or not raw_record[field]:
                raise CatalogError(f"record {record_id} is missing {field}")
        pointer_index = raw_record.get("pointer_index")
        if not isinstance(pointer_index, int) or pointer_index < 0:
            raise CatalogError(f"record {record_id} has invalid pointer_index")
        records.append(
            {
                "id": record_id,
                "context": raw_record["context"],
                "pointer_index": pointer_index,
                "pointer_rom_offset": raw_record["pointer_rom_offset"],
                "record_rom_offset": raw_record["record_rom_offset"],
                "expected_length": expected_length,
                "expected_original": original,
                "encoded": encoded,
                "expected_original_hex": original.hex(" ").upper(),
                "encoded_hex": encoded.hex(" ").upper(),
                "korean_text": raw_record["korean_text"],
                "japanese_source": raw_record.get("japanese_source", ""),
                "translation_basis": raw_record.get("translation_basis", ""),
                "status": raw_record.get("status", "needs_review"),
                "glyph_count": sum(1 for token in raw_record["tokens"] if "glyph" in token),
            }
        )
    source = path.read_bytes()
    return {
        "batch_id": catalog["batch_id"],
        "catalog_path": str(path),
        "catalog_sha256": hashlib.sha256(source).hexdigest(),
        "translation_basis": catalog.get("translation_basis", ""),
        "available_glyph_codes": list(AVAILABLE_GLYPH_CODES),
        "glyph_codes": glyph_codes,
        "records": records,
    }


def report_payload(compiled: dict[str, object]) -> dict[str, object]:
    records = compiled["records"]
    assert isinstance(records, list)
    return {
        "status": "CATALOG_COMPILED_NOT_RELEASE_APPROVED",
        "batch_id": compiled["batch_id"],
        "catalog_path": compiled["catalog_path"],
        "catalog_sha256": compiled["catalog_sha256"],
        "translation_basis": compiled["translation_basis"],
        "glyph_codes": {glyph: f"0x{code:02X}" for glyph, code in compiled["glyph_codes"].items()},
        "reserved_glyph_codes": [f"0x{code:02X}" for code in sorted(RESERVED_GLYPH_CODES)],
        "available_slot_count": len(AVAILABLE_GLYPH_CODES),
        "records": [
            {
                key: value
                for key, value in record.items()
                if key not in {"encoded", "expected_original"}
            }
            for record in records
        ],
    }


def render_markdown(payload: dict[str, object]) -> str:
    records = payload["records"]
    assert isinstance(records, list)
    lines = [
        "# Korean Scene-Batch Compilation",
        "",
        f"Status: **{payload['status']}**",
        "",
        f"- Batch: `{payload['batch_id']}`",
        f"- Catalog SHA-256: `{payload['catalog_sha256']}`",
        f"- Verified glyph slots available: `{payload['available_slot_count']}`",
        f"- Reserved renderer codes: `{', '.join(payload['reserved_glyph_codes'])}`",
        f"- Translation basis: {payload['translation_basis']}",
        "",
        "| id | pointer | record | bytes | glyphs | Korean text | status |",
        "| --- | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| `{record['id']}` | {record['pointer_index']} | `{record['record_rom_offset']}` | "
            f"{record['expected_length']} | {record['glyph_count']} | {record['korean_text']} | {record['status']} |"
        )
    lines += [
        "",
        "All non-glyph bytes were supplied as explicit catalog tokens. The compiler",
        "does not infer controls, relocate pointers, or grant release approval.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    compiled = compile_catalog(args.catalog)
    payload = report_payload(compiled)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"batch={payload['batch_id']}")
    print(f"records={len(payload['records'])}")
    print(f"glyphs={len(payload['glyph_codes'])}")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

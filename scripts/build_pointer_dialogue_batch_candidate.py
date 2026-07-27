#!/usr/bin/env python3
"""Build a bounded multi-record Korean pointer-dialogue candidate.

This is the first non-opening batch that follows the English patch's useful
structural idea: records are catalogued independently, packed at declared
Bank-1 CPU addresses, and only their declared pointer entries are changed.
English wording is never copied into the ROM. Korean glyphs are rendered into
the locally-proven paired 16x16 dialogue path, while all control bytes remain
explicit catalog tokens.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_reference_ips import parse_ips
from build_opening_dialogue_16x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_SIZE,
    _assert_scoped_changes,
    apply_paired_renderer_assets,
    build_square_glyph_tiles,
    changed_spans,
    default_square_font,
    source_codes_for_pairs,
    validate_english_reference_source_slots,
)
from build_opening_dialogue_proof import BASE_MD5, resolve_base_rom
from build_patch import make_records, write_ips
from compile_korean_scene_batch import CatalogError, parse_hex_byte, parse_hex_bytes
from korean_tile_font import square_font_profile, write_square_preview
from paired_dialogue_helper import build_record_scoped_paired_helper
from rom_utils import REPO_ROOT


BANK1_ROM_START = 0x04010
BANK1_CPU_START = 0x8000
POINTER_TABLE_ROM_OFFSET = 0x05DD4
POINTER_TABLE_ENTRY_COUNT = 248
CONTROL_BYTES = frozenset({0x00, 0xBB, 0xCA, 0xF8, 0xF9, 0xFF})

DEFAULT_CATALOG = REPO_ROOT / "text_data" / "korean_scene_batches" / "pointer_dialogue_ptr_002_003.json"
DEFAULT_REFERENCE_IPS = REPO_ROOT / "tools" / "reference" / "TSe-v10.ips"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "pointer_dialogue_batch_002_003"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003_font_preview.png"
DEFAULT_OUT_STEM = "kunio_period_drama_korean_pointer_dialogue_batch_002_003"


def report_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def parse_hex_address(value: object, *, field: str) -> int:
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        token = value.strip().lower()
        if token.startswith("0x"):
            token = token[2:]
        try:
            parsed = int(token, 16)
        except ValueError as exc:
            raise CatalogError(f"{field} is not a hexadecimal address") from exc
    else:
        raise CatalogError(f"{field} must be a hexadecimal address")
    if not 0 <= parsed <= 0xFFFF:
        raise CatalogError(f"{field} is outside the CPU address range")
    return parsed


def bank1_rom_to_cpu(rom_offset: int) -> int:
    return rom_offset - BANK1_ROM_START + BANK1_CPU_START


def parse_source_ranges(raw: object) -> tuple[tuple[int, int], ...]:
    if not isinstance(raw, list) or not raw:
        raise CatalogError("capacity_profile.source_ranges must be a non-empty list")
    ranges: list[tuple[int, int]] = []
    previous_end = -1
    for item in raw:
        if not isinstance(item, list) or len(item) != 2:
            raise CatalogError("each source range must contain start and end")
        start = parse_hex_byte(item[0])
        end = parse_hex_byte(item[1])
        if not start < end or start <= previous_end:
            raise CatalogError("source ranges must be sorted and non-overlapping")
        ranges.append((start, end))
        previous_end = end - 1
    return tuple(ranges)


def parse_glyph_pairs(raw: object) -> dict[str, tuple[int, int]]:
    if not isinstance(raw, dict) or not raw:
        raise CatalogError("capacity_profile.glyph_code_pairs must be non-empty")
    pairs: dict[str, tuple[int, int]] = {}
    used: set[int] = set()
    for glyph, value in raw.items():
        if not isinstance(glyph, str) or len(glyph) != 1:
            raise CatalogError("glyph keys must contain one character")
        if not isinstance(value, list) or len(value) != 2:
            raise CatalogError(f"glyph {glyph!r} needs two source codes")
        left, right = (parse_hex_byte(item) for item in value)
        if left == right or left in used or right in used:
            raise CatalogError(f"glyph {glyph!r} reuses a source code")
        if left in CONTROL_BYTES or right in CONTROL_BYTES:
            raise CatalogError(f"glyph {glyph!r} consumes a renderer control")
        pairs[glyph] = (left, right)
        used.update((left, right))
    return pairs


def encode_tokens(raw: object, pairs: dict[str, tuple[int, int]]) -> bytes:
    if not isinstance(raw, list) or not raw:
        raise CatalogError("record tokens must be a non-empty list")
    encoded = bytearray()
    for index, token in enumerate(raw):
        if not isinstance(token, dict):
            raise CatalogError(f"token {index} must be an object")
        has_glyph = "glyph_pair" in token
        has_byte = "byte" in token
        if has_glyph == has_byte:
            raise CatalogError(f"token {index} must contain exactly one glyph_pair or byte")
        if has_glyph:
            glyph = token["glyph_pair"]
            if glyph not in pairs:
                raise CatalogError(f"token {index} references an unallocated glyph")
            encoded.extend(pairs[glyph])
        else:
            encoded.append(parse_hex_byte(token["byte"]))
    if encoded[-1] != 0xFF or 0xFF in encoded[:-1]:
        raise CatalogError("each record must have exactly one final 0xFF")
    return bytes(encoded)


def pointer_cpu(base: bytes, index: int) -> int:
    offset = POINTER_TABLE_ROM_OFFSET + index * 2
    return int.from_bytes(base[offset:offset + 2], "little")


def pointer_owners(base: bytes, cpu_address: int) -> list[int]:
    return [index for index in range(POINTER_TABLE_ENTRY_COUNT) if pointer_cpu(base, index) == cpu_address]


def load_catalog(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(f"invalid JSON catalog: {path}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise CatalogError("unsupported pointer batch catalog")
    if not isinstance(payload.get("records"), list) or not payload["records"]:
        raise CatalogError("pointer batch catalog needs records")
    return payload


def validate_catalog(path: Path, base: bytes) -> dict[str, object]:
    catalog = load_catalog(path)
    pairs = parse_glyph_pairs(catalog.get("capacity_profile", {}).get("glyph_code_pairs"))
    ranges = parse_source_ranges(catalog.get("capacity_profile", {}).get("source_ranges"))
    source_codes = source_codes_for_pairs(pairs)
    if any(not any(start <= code < end for start, end in ranges) for code in source_codes):
        raise CatalogError("a glyph source code is outside the declared helper ranges")
    guard = catalog.get("record_guard")
    if not isinstance(guard, dict) or guard.get("kind") != "record_list":
        raise CatalogError("record_list guard is required")
    expected_indices = guard.get("expected_pointer_indices")
    if not isinstance(expected_indices, list) or not expected_indices:
        raise CatalogError("record guard must list pointer indices")

    records: list[dict[str, object]] = []
    encoded_records: list[bytes] = []
    for ordinal, raw in enumerate(catalog["records"]):
        if not isinstance(raw, dict):
            raise CatalogError(f"record {ordinal} must be an object")
        index = raw.get("pointer_index")
        if not isinstance(index, int) or not 0 <= index < POINTER_TABLE_ENTRY_COUNT:
            raise CatalogError(f"record {ordinal} has invalid pointer_index")
        pointer_offset = parse_hex_address(raw.get("pointer_rom_offset"), field=f"record {ordinal} pointer_rom_offset")
        original_record_offset = parse_hex_address(raw.get("original_record_rom_offset"), field=f"record {ordinal} original_record_rom_offset")
        record_offset = parse_hex_address(raw.get("record_rom_offset"), field=f"record {ordinal} record_rom_offset")
        original = parse_hex_bytes(raw.get("expected_original_bytes"), field=f"record {ordinal} expected_original_bytes")
        encoded = parse_hex_bytes(raw.get("expected_encoded_bytes"), field=f"record {ordinal} expected_encoded_bytes")
        old_cpu = parse_hex_address(raw.get("old_pointer_cpu"), field=f"record {ordinal} old_pointer_cpu")
        new_cpu = parse_hex_address(raw.get("new_pointer_cpu"), field=f"record {ordinal} new_pointer_cpu")
        if pointer_offset != POINTER_TABLE_ROM_OFFSET + index * 2:
            raise CatalogError(f"record {ordinal} pointer offset does not match index")
        if len(original) == 0 or len(encoded) == 0 or encoded[-1] != 0xFF:
            raise CatalogError(f"record {ordinal} has invalid byte data")
        if new_cpu != bank1_rom_to_cpu(record_offset):
            raise CatalogError(f"record {ordinal} new pointer does not map to its ROM offset")
        if not isinstance(raw.get("tokens"), list):
            raise CatalogError(f"record {ordinal} is missing tokens")
        token_encoded = encode_tokens(raw["tokens"], pairs)
        if token_encoded != encoded:
            raise CatalogError(f"record {ordinal} token encoding disagrees with expected bytes")
        records.append({
            "id": raw.get("id", f"record-{ordinal}"),
            "pointer_index": index,
            "pointer_rom_offset": pointer_offset,
            "original_record_rom_offset": original_record_offset,
            "record_rom_offset": record_offset,
            "expected_original": original,
            "encoded": encoded,
            "old_pointer_cpu": old_cpu,
            "new_pointer_cpu": new_cpu,
            "korean_text": raw.get("korean_text", ""),
            "english_reference": raw.get("english_reference", ""),
            "japanese_context": raw.get("japanese_context", ""),
            "translation_status": raw.get("translation_status", "unknown"),
        })
        encoded_records.append(encoded)

    if [int(record["pointer_index"]) for record in records] != expected_indices:
        raise CatalogError("record order does not match the declared pointer guard")
    high_bytes = {int(record["new_pointer_cpu"]) >> 8 for record in records}
    if len(high_bytes) != 1:
        raise CatalogError("record-scoped helper requires one new CPU high byte")
    if any(int(record["old_pointer_cpu"]) != pointer_cpu(base, int(record["pointer_index"])) for record in records):
        raise CatalogError("base pointer bytes disagree with the catalog")
    if any(base[int(record["original_record_rom_offset"]):int(record["original_record_rom_offset"]) + len(record["expected_original"])] != record["expected_original"] for record in records):
        raise CatalogError("base record bytes disagree with the catalog")
    for record in records:
        old_cpu = int(record["old_pointer_cpu"])
        new_cpu = int(record["new_pointer_cpu"])
        owners = pointer_owners(base, old_cpu)
        if old_cpu != new_cpu and owners != [int(record["pointer_index"])] :
            raise CatalogError(f"moved record has unexpected old pointer owners: {record['id']}")
        new_owners = pointer_owners(base, new_cpu)
        if new_owners and new_owners != [int(record["pointer_index"])] :
            raise CatalogError(f"new pointer collides with an existing owner: {record['id']}")
    spans = sorted((int(record["record_rom_offset"]), int(record["record_rom_offset"]) + len(record["encoded"]), record) for record in records)
    for (_, end, _), (start, _, _) in zip(spans, spans[1:]):
        if end > start:
            raise CatalogError("packed candidate records overlap")
    for protected in catalog.get("protected_pointers", []):
        if not isinstance(protected, dict):
            raise CatalogError("protected pointer entry must be an object")
        index = protected.get("pointer_index")
        expected_cpu = parse_hex_address(protected.get("expected_pointer_cpu"), field="protected pointer CPU")
        if not isinstance(index, int) or pointer_cpu(base, index) != expected_cpu:
            raise CatalogError("protected pointer does not match the base ROM")
        for start, end, _ in spans:
            if start < BANK1_ROM_START + expected_cpu - BANK1_CPU_START + 1 and end > BANK1_ROM_START + expected_cpu - BANK1_CPU_START:
                raise CatalogError("candidate record reaches a protected pointer's record start")
    source = path.read_bytes()
    return {
        "catalog_path": report_path(path),
        "catalog_sha256": hashlib.sha256(source).hexdigest(),
        "batch_id": catalog.get("batch_id", ""),
        "translation_basis": catalog.get("translation_basis", ""),
        "font_profile": catalog.get("font_profile", "readable"),
        "source_ranges": ranges,
        "glyph_code_pairs": pairs,
        "source_codes": source_codes,
        "english_reference_source_codes": tuple(parse_hex_byte(item) for item in catalog.get("capacity_profile", {}).get("english_reference_source_codes", [])),
        "records": records,
        "encoded_records": encoded_records,
    }


def apply_candidate(base: bytes, config: dict[str, object], glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]]) -> tuple[bytes, list[dict[str, object]], object]:
    records = config["records"]
    pairs = config["glyph_code_pairs"]
    ranges = config["source_ranges"]
    assert isinstance(records, list) and isinstance(pairs, dict) and isinstance(ranges, tuple)
    helper = build_record_scoped_paired_helper(
        record_cpu_addresses=tuple(int(record["new_pointer_cpu"]) for record in records),
        source_ranges=ranges,
        entry_cpu=CODE_CAVE_CPU,
        max_size=CODE_CAVE_SIZE,
    )
    renderer_patched, targets = apply_paired_renderer_assets(
        base,
        glyph_tiles,
        glyph_code_pairs=pairs,
        helper_code=helper.code,
        helper_start_code=ranges[0][0],
        helper_end_code_exclusive=ranges[-1][1],
        source_ranges=ranges,
        marker_helper_cpu=helper.marker_cpu,
    )
    patched = bytearray(renderer_patched)
    for record in records:
        offset = int(record["record_rom_offset"])
        encoded = record["encoded"]
        assert isinstance(encoded, bytes)
        patched[offset:offset + len(encoded)] = encoded
        targets.append({
            "kind": "dialogue_record",
            "rom_offset": offset,
            "length": len(encoded),
            "pointer_index": record["pointer_index"],
            "cpu_address": f"0x{int(record['new_pointer_cpu']):04X}",
        })
    for record in records:
        if int(record["old_pointer_cpu"]) == int(record["new_pointer_cpu"]):
            continue
        offset = int(record["pointer_rom_offset"])
        patched[offset:offset + 2] = int(record["new_pointer_cpu"]).to_bytes(2, "little")
        targets.append({
            "kind": "dialogue_pointer",
            "rom_offset": offset,
            "length": 2,
            "pointer_index": record["pointer_index"],
            "original_cpu_address": f"0x{int(record['old_pointer_cpu']):04X}",
            "new_cpu_address": f"0x{int(record['new_pointer_cpu']):04X}",
        })
    _assert_scoped_changes(base, bytes(patched), targets, label="pointer dialogue batch")
    return bytes(patched), targets, helper


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    records = source["records"]
    lines = [
        "# Pointer Dialogue Batch 002-003",
        "",
        "Status: **CANDIDATE_BUILT_RUNTIME_UNKNOWN**",
        "",
        "This is a soft-gate candidate, not a release patch. It applies two",
        "English-reference-guided Korean dialogue records outside the opening.",
        "PTR-003 is deliberately relocated and its pointer is updated.",
        "",
        "## Scope",
        "",
        f"- Batch: `{source['batch_id']}`.",
        f"- Glyph pairs: `{len(source['glyph_code_pairs'])}`; source ranges: `{source['source_ranges']}`.",
        f"- Renderer helper: `{source['helper_length']}` bytes at `{source['helper_cpu']}`.",
        "- Controls remain explicit; English wording is not written to the ROM.",
        "",
        "| pointer | old CPU | new CPU | ROM record | encoded bytes | Korean draft | runtime |",
        "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| {record['pointer_index']} | `{record['old_pointer_cpu']}` | `{record['new_pointer_cpu']}` | "
            f"`{record['record_rom_offset']}` | {record['encoded_length']} | {record['korean_text']} | UNKNOWN |"
        )
    lines += [
        "",
        "## Candidate",
        "",
        f"- Base MD5: `{candidate['base_md5']}`.",
        f"- Candidate MD5: `{candidate['patched_md5']}`.",
        f"- IPS: `{candidate['ips_path']}`.",
        f"- Changed spans: `{candidate['changed_span_count']}`; escaped bytes: `{candidate['escaped_byte_count']}`.",
        "",
        "## Runtime Gate",
        "",
        "- Verdict: **UNKNOWN**.",
        "- Reason: the bounded FCEUX target for this early-boss dialogue has no",
        "  proven route or save-state entry yet. This avoids returning to an",
        "  untargeted opening/title loop.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--reference-ips", type=Path, default=DEFAULT_REFERENCE_IPS)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--font", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--out-stem", default=DEFAULT_OUT_STEM)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    args = parser.parse_args()

    rom_path = resolve_base_rom(args.rom)
    base = rom_path.read_bytes()
    actual_md5 = hashlib.md5(base).hexdigest()
    if actual_md5 != BASE_MD5:
        raise ValueError(f"unsupported base ROM MD5: {actual_md5}")
    if not args.reference_ips.is_file():
        raise FileNotFoundError(f"reference IPS not found: {args.reference_ips}")
    config = validate_catalog(args.catalog, base)
    font = default_square_font(args.font)
    font_profile = str(config["font_profile"])
    settings = square_font_profile(font_profile)
    pairs = config["glyph_code_pairs"]
    assert isinstance(pairs, dict)
    glyph_tiles = build_square_glyph_tiles(font, pairs, font_profile=font_profile)
    patched, targets, helper = apply_candidate(base, config, glyph_tiles)
    reference = validate_english_reference_source_slots(
        base,
        args.reference_ips,
        source_codes=tuple(int(code) for code in config["english_reference_source_codes"]),
    )
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{args.out_stem}.ips"
    rom_path_out = args.out_dir / f"{args.out_stem}.nes"
    write_ips(ips_path, records)
    rom_path_out.write_bytes(patched)
    write_square_preview(
        list(pairs),
        args.preview,
        font_path=font,
        target_pixels=int(settings["target_pixels"]),
        threshold=int(settings["threshold"]),
        resample=str(settings["resample"]),
    )
    source_records = []
    for record in config["records"]:
        source_records.append({
            "id": record["id"],
            "pointer_index": record["pointer_index"],
            "old_pointer_cpu": f"0x{int(record['old_pointer_cpu']):04X}",
            "new_pointer_cpu": f"0x{int(record['new_pointer_cpu']):04X}",
            "record_rom_offset": f"0x{int(record['record_rom_offset']):05X}",
            "encoded_length": len(record["encoded"]),
            "korean_text": record["korean_text"],
            "english_reference": record["english_reference"],
            "translation_status": record["translation_status"],
        })
    payload = {
        "status": "CANDIDATE_BUILT_RUNTIME_UNKNOWN",
        "source": {
            "base_md5": BASE_MD5,
            "batch_id": config["batch_id"],
            "catalog": config["catalog_path"],
            "catalog_sha256": config["catalog_sha256"],
            "reference_ips": report_path(args.reference_ips),
            "reference_validation": reference,
            "font": str(font),
            "font_profile": font_profile,
            "font_preview": report_path(args.preview),
            "glyph_code_pairs": {glyph: [f"0x{left:02X}", f"0x{right:02X}"] for glyph, (left, right) in pairs.items()},
            "source_ranges": [f"0x{start:02X}-0x{end - 1:02X}" for start, end in config["source_ranges"]],
            "helper_length": len(helper.code),
            "helper_cpu": f"0x{helper.entry_cpu:04X}",
            "records": source_records,
        },
        "candidate": {
            "base_md5": actual_md5,
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": report_path(ips_path),
            "rom_path": report_path(rom_path_out),
            "ips_record_count": len(records),
            "changed_span_count": len(changed_spans(base, patched)),
            "escaped_byte_count": 0,
            "targets": targets,
        },
        "runtime_gate": {
            "verdict": "UNKNOWN",
            "reason": "No bounded early-boss route or save-state entry is proven yet.",
            "opening_regression": "not_run",
            "pointer_2_visible": "unknown",
            "pointer_3_visible": "unknown",
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"rom={rom_path_out}")
    print(f"ips={ips_path}")
    print(f"report_json={args.report_json}")
    print(f"candidate_md5={payload['candidate']['patched_md5']}")
    print("runtime_gate=UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

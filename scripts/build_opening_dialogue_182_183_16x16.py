#!/usr/bin/env python3
"""Build a readable, two-record Korean opening-dialogue candidate.

This candidate is deliberately small but moves beyond a one-record font demo:
it keeps pointers 182 and 183 in the same verified opening scene, allocates a
19-syllable 16x16 pool, preserves renderer controls outside explicit source
ranges, and packs the two records without overwriting pointer 184.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_opening_dialogue_16x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_SIZE,
    _assert_scoped_changes,
    add_target,
    apply_paired_renderer_assets,
    build_square_glyph_tiles,
    changed_spans,
    default_square_font,
    encode_pair_tokens,
    source_codes_for_pairs,
    validate_english_reference_source_slots,
)
from build_opening_dialogue_proof import BASE_MD5, CHR_BANK, resolve_base_rom
from build_patch import make_records, write_ips
from compile_korean_scene_batch import CatalogError, load_catalog, parse_hex_byte, parse_hex_bytes
from korean_tile_font import square_font_profile, write_square_preview
from paired_dialogue_helper import build_record_scoped_paired_helper
from rom_utils import REPO_ROOT


BANK1_ROM_START = 0x04010
BANK1_CPU_START = 0x8000
POINTER_TABLE_ROM_OFFSET = 0x05DD4
POINTER_TABLE_ENTRY_COUNT = 248
PRIMARY_POINTER_INDEX = 182
FOLLOWING_POINTER_INDEX = 183
NEXT_POINTER_INDEX = 184

DEFAULT_CATALOG = REPO_ROOT / "text_data" / "korean_scene_batches" / "opening_ptr_182_183_16x16_readability.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_ptr_182_183_16x16_readability"
DEFAULT_OUT_STEM = "kunio_period_drama_korean_opening_ptr_182_183_16x16_readability"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_ptr_182_183_16x16_readability.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_ptr_182_183_16x16_readability.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_ptr_182_183_16x16_readability_font_preview.png"


def report_path(path: Path) -> str:
    """Use repository-relative report paths whenever the artifact is local."""

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
            raise CatalogError(f"{field} is not a hexadecimal address: {value!r}") from exc
    else:
        raise CatalogError(f"{field} must be a hexadecimal address")
    if not 0 <= parsed <= 0xFFFFF:
        raise CatalogError(f"{field} is outside ROM address bounds")
    return parsed


def bank1_rom_to_cpu(rom_offset: int) -> int:
    """Map a header-inclusive Bank-1 ROM offset to its CPU address."""

    return rom_offset - BANK1_ROM_START + BANK1_CPU_START


def bank1_cpu_to_rom(cpu_address: int) -> int:
    """Map a Bank-1 CPU address back to its header-inclusive ROM offset."""

    return cpu_address - BANK1_CPU_START + BANK1_ROM_START


def parse_source_ranges(raw: object) -> tuple[tuple[int, int], ...]:
    if not isinstance(raw, list) or not raw:
        raise CatalogError("capacity_profile.source_ranges must be a non-empty list")
    ranges: list[tuple[int, int]] = []
    previous_end = -1
    for index, item in enumerate(raw):
        if not isinstance(item, list) or len(item) != 2:
            raise CatalogError(f"source range {index} must contain start and end-exclusive bytes")
        start = parse_hex_byte(item[0])
        end = parse_hex_byte(item[1])
        if start >= end:
            raise CatalogError(f"source range {index} is empty or reversed")
        if start <= previous_end:
            raise CatalogError("source ranges must be sorted and non-overlapping")
        ranges.append((start, end))
        previous_end = end - 1
    return tuple(ranges)


def parse_glyph_pairs(raw: object) -> dict[str, tuple[int, int]]:
    if not isinstance(raw, dict) or not raw:
        raise CatalogError("capacity_profile.glyph_code_pairs must be a non-empty object")
    pairs: dict[str, tuple[int, int]] = {}
    used_codes: set[int] = set()
    for glyph, value in raw.items():
        if not isinstance(glyph, str) or len(glyph) != 1:
            raise CatalogError("glyph_code_pairs keys must each be one character")
        if not isinstance(value, list) or len(value) != 2:
            raise CatalogError(f"glyph {glyph!r} must own exactly two source codes")
        left, right = (parse_hex_byte(item) for item in value)
        if left == right or left in used_codes or right in used_codes:
            raise CatalogError(f"glyph {glyph!r} reuses a source code")
        pairs[glyph] = (left, right)
        used_codes.update((left, right))
    return pairs


def source_in_ranges(code: int, ranges: tuple[tuple[int, int], ...]) -> bool:
    return any(start <= code < end for start, end in ranges)


def parse_record(raw: object, *, ordinal: int) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise CatalogError(f"record {ordinal} must be an object")
    pointer_index = raw.get("pointer_index")
    if not isinstance(pointer_index, int) or not 0 <= pointer_index < POINTER_TABLE_ENTRY_COUNT:
        raise CatalogError(f"record {ordinal} has an invalid pointer_index")
    expected_length = raw.get("expected_length")
    if not isinstance(expected_length, int) or expected_length <= 0:
        raise CatalogError(f"record {ordinal} needs a positive expected_length")
    parsed = {
        "id": raw.get("id"),
        "pointer_index": pointer_index,
        "pointer_rom_offset": parse_hex_address(raw.get("pointer_rom_offset"), field=f"record {ordinal} pointer_rom_offset"),
        "record_rom_offset": parse_hex_address(raw.get("record_rom_offset"), field=f"record {ordinal} record_rom_offset"),
        "expected_base_bytes": parse_hex_bytes(raw.get("expected_base_bytes"), field=f"record {ordinal} expected_base_bytes"),
        "old_pointer_cpu": parse_hex_address(raw.get("old_pointer_cpu"), field=f"record {ordinal} old_pointer_cpu"),
        "new_pointer_cpu": parse_hex_address(raw.get("new_pointer_cpu"), field=f"record {ordinal} new_pointer_cpu"),
        "expected_length": expected_length,
        "tokens": raw.get("tokens"),
        "korean_text": raw.get("korean_text"),
        "japanese_context": raw.get("japanese_context"),
    }
    if not isinstance(parsed["id"], str) or not parsed["id"]:
        raise CatalogError(f"record {ordinal} needs an id")
    if not isinstance(parsed["korean_text"], str) or not parsed["korean_text"]:
        raise CatalogError(f"record {ordinal} needs Korean text")
    if len(parsed["expected_base_bytes"]) != expected_length:
        raise CatalogError(f"record {ordinal} expected_base_bytes length does not equal expected_length")
    if parsed["pointer_rom_offset"] != POINTER_TABLE_ROM_OFFSET + pointer_index * 2:
        raise CatalogError(f"record {ordinal} pointer table offset does not match index")
    if parsed["new_pointer_cpu"] != bank1_rom_to_cpu(int(parsed["record_rom_offset"])):
        raise CatalogError(f"record {ordinal} new_pointer_cpu does not map to record_rom_offset")
    return parsed


def validate_catalog(catalog_path: Path) -> dict[str, object]:
    catalog = load_catalog(catalog_path)
    if catalog.get("batch_id") != "opening_ptr_182_183_16x16_readability":
        raise CatalogError("unexpected two-record opening catalog id")
    if catalog.get("renderer_profile") != "record_scoped_paired_8x16_cells_for_16x16_korean":
        raise CatalogError("unexpected renderer profile")
    font_profile = catalog.get("font_profile", "readable")
    if not isinstance(font_profile, str):
        raise CatalogError("font_profile must be a named profile")
    square_font_profile(font_profile)

    capacity = catalog.get("capacity_profile")
    if not isinstance(capacity, dict):
        raise CatalogError("capacity_profile must be an object")
    ranges = parse_source_ranges(capacity.get("source_ranges"))
    pairs = parse_glyph_pairs(capacity.get("glyph_code_pairs"))
    source_codes = source_codes_for_pairs(pairs)
    if any(not source_in_ranges(code, ranges) for code in source_codes):
        raise CatalogError("glyph source code falls outside a declared helper range")
    if any(code == 0xBB for code in source_codes):
        raise CatalogError("0xBB stays a renderer-special control and cannot be a glyph half")
    english_raw = capacity.get("english_reference_source_codes")
    if not isinstance(english_raw, list) or not english_raw:
        raise CatalogError("english_reference_source_codes must be a non-empty list")
    english_codes = tuple(parse_hex_byte(value) for value in english_raw)
    if len(set(english_codes)) != len(english_codes) or not set(english_codes) <= set(source_codes):
        raise CatalogError("English reference source codes must be unique allocated source slots")

    raw_records = catalog["records"]
    assert isinstance(raw_records, list)
    if len(raw_records) != 2:
        raise CatalogError("two-record opening catalog must contain exactly two records")
    records = [parse_record(raw, ordinal=index) for index, raw in enumerate(raw_records)]
    primary, following = records
    if primary["pointer_index"] != PRIMARY_POINTER_INDEX or following["pointer_index"] != FOLLOWING_POINTER_INDEX:
        raise CatalogError("records must be pointer 182 followed by pointer 183")
    encoded_records: list[bytes] = []
    used_glyphs: list[str] = []
    for index, record in enumerate(records):
        encoded, glyphs = encode_pair_tokens(record["tokens"], pairs)
        expected_encoded = parse_hex_bytes(raw_records[index].get("expected_encoded_bytes"), field=f"record {index} expected_encoded_bytes")
        if encoded != expected_encoded or len(encoded) != record["expected_length"]:
            raise CatalogError(f"record {index} token encoding disagrees with its expected bytes")
        if encoded[-1] != 0xFF or 0xFF in encoded[:-1]:
            raise CatalogError(f"record {index} has an invalid terminator layout")
        encoded_records.append(encoded)
        for glyph in glyphs:
            if glyph not in used_glyphs:
                used_glyphs.append(glyph)
    if set(used_glyphs) != set(pairs):
        raise CatalogError("two-record catalog must exercise every allocated glyph")
    if int(following["record_rom_offset"]) != int(primary["record_rom_offset"]) + len(encoded_records[0]):
        raise CatalogError("pointer 183 must begin immediately after the shortened pointer-182 record")
    if int(primary["old_pointer_cpu"]) != int(primary["new_pointer_cpu"]):
        raise CatalogError("pointer 182 is expected to retain its base table pointer")
    if int(following["old_pointer_cpu"]) == int(following["new_pointer_cpu"]):
        raise CatalogError("pointer 183 must explicitly move to its packed record start")

    protected = catalog.get("protected_next_pointer")
    if not isinstance(protected, dict):
        raise CatalogError("protected_next_pointer is required")
    protected_index = protected.get("pointer_index")
    if protected_index != NEXT_POINTER_INDEX:
        raise CatalogError("protected_next_pointer must identify pointer 184")
    protected_cpu = parse_hex_address(protected.get("expected_pointer_cpu"), field="protected_next_pointer expected_pointer_cpu")
    source = catalog_path.read_bytes()
    return {
        "catalog_path": report_path(catalog_path),
        "catalog_sha256": hashlib.sha256(source).hexdigest(),
        "batch_id": catalog["batch_id"],
        "font_profile": font_profile,
        "source_ranges": ranges,
        "glyph_code_pairs": pairs,
        "source_codes": source_codes,
        "english_codes": english_codes,
        "records": records,
        "encoded_records": encoded_records,
        "used_glyphs": used_glyphs,
        "protected_next_pointer_cpu": protected_cpu,
    }


def pointer_cpu(base: bytes, index: int) -> int:
    offset = POINTER_TABLE_ROM_OFFSET + index * 2
    return int.from_bytes(base[offset:offset + 2], "little")


def pointer_owners(base: bytes, cpu_address: int) -> list[int]:
    return [index for index in range(POINTER_TABLE_ENTRY_COUNT) if pointer_cpu(base, index) == cpu_address]


def apply_candidate(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
    config: dict[str, object],
) -> tuple[bytes, list[dict[str, object]], object]:
    records = config["records"]
    encoded_records = config["encoded_records"]
    pairs = config["glyph_code_pairs"]
    ranges = config["source_ranges"]
    assert isinstance(records, list) and isinstance(encoded_records, list)
    assert isinstance(pairs, dict) and isinstance(ranges, tuple)
    primary, following = records
    primary_bytes, following_bytes = encoded_records
    assert isinstance(primary_bytes, bytes) and isinstance(following_bytes, bytes)

    for record in records:
        offset = int(record["record_rom_offset"])
        expected = record["expected_base_bytes"]
        assert isinstance(expected, bytes)
        if base[offset:offset + len(expected)] != expected:
            raise ValueError(f"base bytes do not match catalog for {record['id']}")
        if pointer_cpu(base, int(record["pointer_index"])) != int(record["old_pointer_cpu"]):
            raise ValueError(f"base pointer does not match catalog for {record['id']}")
    if pointer_owners(base, int(following["old_pointer_cpu"])) != [FOLLOWING_POINTER_INDEX]:
        raise ValueError("pointer 183 base record has unexpected additional owners")
    if pointer_cpu(base, NEXT_POINTER_INDEX) != int(config["protected_next_pointer_cpu"]):
        raise ValueError("pointer 184 differs from the protected base pointer")
    following_end = int(following["record_rom_offset"]) + len(following_bytes)
    if following_end != bank1_cpu_to_rom(int(config["protected_next_pointer_cpu"])):
        raise ValueError("packed pointer-183 record would overlap pointer 184")

    helper = build_record_scoped_paired_helper(
        record_cpu_addresses=(int(primary["new_pointer_cpu"]), int(following["new_pointer_cpu"])),
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
    for record, encoded in zip(records, encoded_records):
        offset = int(record["record_rom_offset"])
        patched[offset:offset + len(encoded)] = encoded
        add_target(
            targets,
            kind="dialogue_record",
            rom_offset=offset,
            length=len(encoded),
            pointer_index=record["pointer_index"],
            pointer_rom_offset=f"0x{int(record['pointer_rom_offset']):05X}",
            cpu_address=f"0x{int(record['new_pointer_cpu']):04X}",
        )
    pointer_offset = int(following["pointer_rom_offset"])
    patched[pointer_offset:pointer_offset + 2] = int(following["new_pointer_cpu"]).to_bytes(2, "little")
    add_target(
        targets,
        kind="dialogue_pointer",
        rom_offset=pointer_offset,
        length=2,
        pointer_index=FOLLOWING_POINTER_INDEX,
        original_cpu_address=f"0x{int(following['old_pointer_cpu']):04X}",
        new_cpu_address=f"0x{int(following['new_pointer_cpu']):04X}",
    )
    if pointer_cpu(bytes(patched), NEXT_POINTER_INDEX) != int(config["protected_next_pointer_cpu"]):
        raise AssertionError("pointer 184 changed during the two-record packing step")
    _assert_scoped_changes(base, patched, targets, label="two-record paired 16x16 candidate")
    return bytes(patched), targets, helper


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    lines = [
        "# Two-Record Opening Korean 16x16 Candidate",
        "",
        "Status: **CANDIDATE_BUILT_NOT_RUNTIME_VERIFIED**",
        "",
        "This candidate packs two context-confirmed opening records without using",
        "unbounded gameplay. It is a font-capacity and record-boundary candidate,",
        "not a release translation batch.",
        "",
        "## Scope",
        "",
        f"- Glyphs: `{source['unique_glyph_count']}` / source slots: `{source['source_slot_count']}`.",
        f"- Source ranges: {', '.join(source['source_ranges'])}.",
        f"- Helper: `{source['helper_length']}` bytes; marker hook `{source['marker_cpu']}`.",
    ]
    for record in source["records"]:
        lines.append(
            f"- Pointer {record['pointer_index']}: `{record['record_rom_offset']}` / "
            f"`{record['cpu_address']}` ({record['record_length']} bytes): {record['korean_text']}"
        )
    lines.extend(
        [
            "",
            "## Result",
            "",
            f"- Base MD5: `{candidate['base_md5']}`",
            f"- Candidate MD5: `{candidate['patched_md5']}`",
            f"- Changed spans: `{candidate['changed_span_count']}`; escaped bytes: `{candidate['escaped_byte_count']}`.",
            f"- IPS: `{candidate['ips_path']}`",
            f"- ROM: `{candidate['rom_path']}`",
            "",
            "Promotion requires the separate bounded pointer-182 and pointer-183",
            "captures, matching runtime reads, and native readability review for both screens.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom")
    parser.add_argument("--reference-ips", required=True, type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--font")
    parser.add_argument("--font-profile")
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
    ips_path = args.reference_ips.expanduser()
    if not ips_path.is_file():
        raise FileNotFoundError(f"reference IPS not found: {ips_path}")
    config = validate_catalog(args.catalog)
    english_codes = config["english_codes"]
    pairs = config["glyph_code_pairs"]
    assert isinstance(english_codes, tuple) and isinstance(pairs, dict)
    reference = validate_english_reference_source_slots(base, ips_path, source_codes=english_codes)
    font = default_square_font(args.font)
    font_profile = args.font_profile or str(config["font_profile"])
    font_settings = square_font_profile(font_profile)
    glyph_tiles = build_square_glyph_tiles(font, pairs, font_profile=font_profile)
    patched, targets, helper = apply_candidate(base, glyph_tiles, config)
    ips_records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_output = args.out_dir / f"{args.out_stem}.ips"
    rom_output = args.out_dir / f"{args.out_stem}.nes"
    write_ips(ips_output, ips_records)
    rom_output.write_bytes(patched)
    write_square_preview(
        list(pairs),
        args.preview,
        font_path=font,
        target_pixels=int(font_settings["target_pixels"]),
        threshold=int(font_settings["threshold"]),
        resample=str(font_settings["resample"]),
    )
    changed = changed_spans(base, patched)
    records = config["records"]
    encoded_records = config["encoded_records"]
    ranges = config["source_ranges"]
    assert isinstance(records, list) and isinstance(encoded_records, list) and isinstance(ranges, tuple)
    payload = {
        "status": "CANDIDATE_BUILT_NOT_RUNTIME_VERIFIED",
        "source": {
            "batch_id": config["batch_id"],
            "base_md5": BASE_MD5,
            "catalog": config["catalog_path"],
            "catalog_sha256": config["catalog_sha256"],
            "font": str(font),
            "font_profile": font_profile,
            "font_profile_settings": font_settings,
            "font_preview": report_path(args.preview),
            "chr_bank": CHR_BANK,
            "unique_glyph_count": len(pairs),
            "source_slot_count": len(config["source_codes"]),
            "source_ranges": [f"0x{start:02X}-0x{end - 1:02X}" for start, end in ranges],
            "helper_length": len(helper.code),
            "marker_cpu": f"0x{helper.marker_cpu:04X}",
            "records": [
                {
                    "id": record["id"],
                    "pointer_index": record["pointer_index"],
                    "pointer_rom_offset": f"0x{int(record['pointer_rom_offset']):05X}",
                    "record_rom_offset": f"0x{int(record['record_rom_offset']):05X}",
                    "cpu_address": f"0x{int(record['new_pointer_cpu']):04X}",
                    "record_length": len(encoded),
                    "korean_text": record["korean_text"],
                    "japanese_context": record["japanese_context"],
                }
                for record, encoded in zip(records, encoded_records)
            ],
            "glyph_code_pairs": {
                glyph: [f"0x{left:02X}", f"0x{right:02X}"]
                for glyph, (left, right) in pairs.items()
            },
        },
        "english_reference_validation": reference,
        "candidate": {
            "base_md5": actual_md5,
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": report_path(ips_output),
            "rom_path": report_path(rom_output),
            "ips_record_count": len(ips_records),
            "changed_span_count": len(changed),
            "changed_spans": [
                {"start": f"0x{start:05X}", "end_exclusive": f"0x{end:05X}"}
                for start, end in changed
            ],
            "escaped_byte_count": 0,
            "targets": targets,
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"ips={ips_output}")
    print(f"rom={rom_output}")
    print(f"report_json={args.report_json}")
    print(f"report_markdown={args.report_markdown}")
    print(f"base_md5={actual_md5}")
    print(f"patched_md5={payload['candidate']['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

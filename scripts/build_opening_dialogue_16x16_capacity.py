#!/usr/bin/env python3
"""Build a bounded paired-8x16 Korean glyph-capacity candidate.

Each catalog owns its source-code pairs, helper range, English-reference
source slots, text record, and output identity. The builder stays limited to
the verified opening pointer record and an explicitly declared overlapping
neighbour relocation, and checks every byte it changes. It is a capacity tool,
not a blanket authorization to overwrite Bank 7 or translate the whole game.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_opening_dialogue_16x16_proof import (
    apply_paired_opening_candidate,
    build_square_glyph_tiles,
    changed_spans,
    default_square_font,
    encode_pair_tokens,
    helper_code_for_range,
    source_codes_for_pairs,
    validate_english_reference_source_slots,
)
from build_opening_dialogue_8x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
)
from build_opening_dialogue_proof import (
    BASE_MD5,
    CHR_BANK,
    ORIGINAL_RECORD,
    POINTER_INDEX,
    POINTER_ROM_OFFSET,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    resolve_base_rom,
)
from build_patch import make_records, write_ips
from compile_korean_scene_batch import CatalogError, load_catalog, parse_hex_byte, parse_hex_bytes
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


DEFAULT_CATALOG = REPO_ROOT / "text_data" / "korean_scene_batches" / "opening_ptr_182_16x16_capacity_tier1.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_dialogue_16x16_capacity_tier1"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_16x16_capacity_tier1.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_16x16_capacity_tier1.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_16x16_capacity_tier1_font_preview.png"
DEFAULT_OUT_STEM = "kunio_period_drama_korean_opening_dialogue_16x16_capacity_tier1"
POINTER_TABLE_ROM_OFFSET = POINTER_ROM_OFFSET - (POINTER_INDEX * 2)
POINTER_TABLE_ENTRY_COUNT = 248


def parse_code_pair(value: object, *, glyph: str) -> tuple[int, int]:
    if not isinstance(value, list) or len(value) != 2:
        raise CatalogError(f"glyph {glyph!r} must own exactly two source codes")
    pair = tuple(parse_hex_byte(part) for part in value)
    if pair[0] == pair[1]:
        raise CatalogError(f"glyph {glyph!r} reuses one source code for both halves")
    return pair


def parse_hex_address(value: object, *, field: str) -> int:
    """Parse a catalog address without allowing an implicit decimal value."""

    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise CatalogError(f"{field} must be a hexadecimal integer")
    token = value.strip().lower()
    if not token.startswith("0x"):
        raise CatalogError(f"{field} must use a 0x-prefixed hexadecimal value")
    try:
        return int(token, 16)
    except ValueError as exc:
        raise CatalogError(f"{field} is not a hexadecimal integer: {value!r}") from exc


def parse_relocation(record: dict[str, Any], *, output_length: int) -> dict[str, object] | None:
    """Validate the one explicitly declared neighbour relocation strategy.

    Expanding pointer 182 overwrites the start of pointer 183's record. The
    only permitted remedy is to copy that exact neighbour into the unused tail
    of the already-approved renderer cave and repoint every base-ROM owner of
    that record. A catalog cannot silently opt into a broader pointer rewrite.
    """

    raw = record.get("relocation")
    if output_length == RECORD_LENGTH:
        if raw is not None:
            raise CatalogError("a fixed-length capacity record must not declare relocation")
        return None
    if output_length < RECORD_LENGTH:
        raise CatalogError("capacity record cannot be shorter than the verified source record")
    if not isinstance(raw, dict):
        raise CatalogError("an expanded capacity record requires a relocation object")

    pointer_index = raw.get("preserved_pointer_index")
    if not isinstance(pointer_index, int) or pointer_index < 0 or pointer_index >= POINTER_TABLE_ENTRY_COUNT:
        raise CatalogError("relocation preserved_pointer_index is outside the verified table")
    pointer_rom_offset = parse_hex_address(
        raw.get("preserved_pointer_rom_offset"), field="relocation preserved_pointer_rom_offset"
    )
    if pointer_rom_offset != POINTER_TABLE_ROM_OFFSET + (pointer_index * 2):
        raise CatalogError("relocation preserved pointer offset does not match its pointer-table index")
    record_rom_offset = parse_hex_address(
        raw.get("preserved_record_rom_offset"), field="relocation preserved_record_rom_offset"
    )
    expected_pointer_cpu = parse_hex_address(
        raw.get("expected_pointer_cpu"), field="relocation expected_pointer_cpu"
    )
    record_length = raw.get("preserved_record_length")
    if not isinstance(record_length, int) or record_length <= 0:
        raise CatalogError("relocation preserved_record_length must be positive")
    expected_indices = raw.get("expected_pointer_indices", [pointer_index])
    if not isinstance(expected_indices, list) or any(
        not isinstance(index, int) or index < 0 or index >= POINTER_TABLE_ENTRY_COUNT
        for index in expected_indices
    ):
        raise CatalogError("relocation expected_pointer_indices must be valid pointer-table indices")
    if expected_indices != [pointer_index]:
        raise CatalogError("the bounded relocation supports exactly one preserved pointer owner")
    return {
        "preserved_pointer_index": pointer_index,
        "preserved_pointer_rom_offset": pointer_rom_offset,
        "preserved_record_rom_offset": record_rom_offset,
        "expected_pointer_cpu": expected_pointer_cpu,
        "preserved_record_length": record_length,
        "expected_pointer_indices": expected_indices,
    }


def parse_capacity_profile(raw: object) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise CatalogError("capacity_profile must be an object")
    pairs_raw = raw.get("glyph_code_pairs")
    if not isinstance(pairs_raw, dict) or not pairs_raw:
        raise CatalogError("capacity_profile glyph_code_pairs must be a non-empty object")
    pairs: dict[str, tuple[int, int]] = {}
    for glyph, value in pairs_raw.items():
        if not isinstance(glyph, str) or len(glyph) != 1:
            raise CatalogError("glyph_code_pairs keys must be one Korean character")
        pairs[glyph] = parse_code_pair(value, glyph=glyph)
    start = parse_hex_byte(raw.get("helper_start_code"))
    end_exclusive = parse_hex_byte(raw.get("helper_end_code_exclusive"))
    helper_code_for_range(start_code=start, end_code_exclusive=end_exclusive)
    english_raw = raw.get("english_reference_source_codes")
    if not isinstance(english_raw, list) or not english_raw:
        raise CatalogError("capacity_profile english_reference_source_codes must be a non-empty list")
    english_codes = tuple(parse_hex_byte(value) for value in english_raw)
    if len(set(english_codes)) != len(english_codes):
        raise CatalogError("English-reference source codes must not repeat")
    source_codes = source_codes_for_pairs(pairs)
    if any(code == 0xBB for code in source_codes):
        raise CatalogError("0xBB is a renderer-special source byte and cannot be a Korean glyph half")
    if not set(english_codes) <= set(source_codes):
        raise CatalogError("English-reference source codes must belong to the glyph-pair allocation")
    return {
        "glyph_code_pairs": pairs,
        "source_codes": source_codes,
        "helper_start_code": start,
        "helper_end_code_exclusive": end_exclusive,
        "english_reference_source_codes": english_codes,
    }


def validate_capacity_catalog(catalog_path: Path) -> dict[str, object]:
    catalog = load_catalog(catalog_path)
    profile = parse_capacity_profile(catalog.get("capacity_profile"))
    records = catalog["records"]
    assert isinstance(records, list)
    if len(records) != 1 or not isinstance(records[0], dict):
        raise CatalogError("capacity catalog must contain exactly one record")
    record = records[0]
    expected_length = record.get("expected_length")
    base_record_length = record.get("base_record_length", RECORD_LENGTH)
    if (
        not isinstance(record.get("id"), str)
        or record.get("pointer_index") != POINTER_INDEX
        or record.get("pointer_rom_offset") != f"0x{POINTER_ROM_OFFSET:05X}"
        or record.get("record_rom_offset") != f"0x{RECORD_ROM_OFFSET:05X}"
        or not isinstance(expected_length, int)
        or expected_length < RECORD_LENGTH
        or base_record_length != RECORD_LENGTH
    ):
        raise CatalogError("capacity catalog does not identify the verified opening record")
    original = parse_hex_bytes(
        record.get("expected_original_bytes"), field="capacity expected_original_bytes"
    )
    if original != ORIGINAL_RECORD:
        raise CatalogError("capacity catalog source bytes diverge from the verified base ROM")
    pairs = profile["glyph_code_pairs"]
    assert isinstance(pairs, dict)
    encoded, glyphs = encode_pair_tokens(record.get("tokens"), pairs)
    expected_encoded = parse_hex_bytes(
        record.get("expected_encoded_bytes"), field="capacity expected_encoded_bytes"
    )
    if encoded != expected_encoded:
        raise CatalogError("capacity catalog tokens diverge from expected_encoded_bytes")
    if len(encoded) != expected_length or encoded[-1] != 0xFF or 0xFF in encoded[:-1]:
        raise CatalogError("capacity record length or terminator is invalid")
    if set(glyphs) != set(pairs) or len(glyphs) != len(pairs):
        raise CatalogError("capacity catalog must use every allocated glyph exactly once or more")
    start = profile["helper_start_code"]
    end_exclusive = profile["helper_end_code_exclusive"]
    assert isinstance(start, int) and isinstance(end_exclusive, int)
    if 0xBB in encoded and start <= 0xBB < end_exclusive:
        raise CatalogError("the helper range would intercept the renderer-special 0xBB byte")
    relocation = parse_relocation(record, output_length=expected_length)
    source = catalog_path.read_bytes()
    return {
        "batch_id": catalog["batch_id"],
        "catalog_path": str(catalog_path),
        "catalog_sha256": hashlib.sha256(source).hexdigest(),
        "record": record,
        "encoded": encoded,
        "base_record_length": base_record_length,
        "relocation": relocation,
        "glyphs": glyphs,
        "profile": profile,
    }


def assert_scoped_changes(base: bytes, patched: bytes, targets: list[dict[str, object]]) -> None:
    allowed = [
        (int(target["rom_offset"]), int(target["rom_offset"]) + int(target["length"]))
        for target in targets
    ]
    escaped = [
        offset
        for offset, (old, new) in enumerate(zip(base, patched))
        if old != new and not any(start <= offset < end for start, end in allowed)
    ]
    if escaped:
        raise AssertionError(f"capacity candidate changed {len(escaped)} byte(s) outside its allowlist")


def apply_capacity_candidate(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
    config: dict[str, object],
) -> tuple[bytes, list[dict[str, object]]]:
    profile = config["profile"]
    assert isinstance(profile, dict)
    pairs = profile["glyph_code_pairs"]
    start = profile["helper_start_code"]
    end_exclusive = profile["helper_end_code_exclusive"]
    assert isinstance(pairs, dict) and isinstance(start, int) and isinstance(end_exclusive, int)
    encoded = config["encoded"]
    relocation = config["relocation"]
    assert isinstance(encoded, bytes)
    patched, targets = apply_paired_opening_candidate(
        base,
        glyph_tiles,
        proof_record=encoded[:RECORD_LENGTH],
        glyph_code_pairs=pairs,
        helper_code=helper_code_for_range(start_code=start, end_code_exclusive=end_exclusive),
        helper_start_code=start,
        helper_end_code_exclusive=end_exclusive,
    )
    if relocation is None:
        return patched, targets

    helper_code = helper_code_for_range(start_code=start, end_code_exclusive=end_exclusive)
    pointer_offset = int(relocation["preserved_pointer_rom_offset"])
    old_pointer_cpu = int.from_bytes(base[pointer_offset:pointer_offset + 2], "little")
    expected_pointer_cpu = int(relocation["expected_pointer_cpu"])
    primary_pointer_cpu = int.from_bytes(
        base[POINTER_ROM_OFFSET:POINTER_ROM_OFFSET + 2], "little"
    )
    old_record_offset = int(relocation["preserved_record_rom_offset"])
    expected_record_cpu = primary_pointer_cpu + (old_record_offset - RECORD_ROM_OFFSET)
    if not 0 <= expected_record_cpu <= 0xFFFF or expected_pointer_cpu != expected_record_cpu:
        raise ValueError("the preserved neighbour ROM offset does not map to its declared CPU pointer")
    if old_pointer_cpu != expected_pointer_cpu:
        raise ValueError("the preserved neighbour pointer does not match the verified base ROM")
    actual_indices = [
        index
        for index in range(POINTER_TABLE_ENTRY_COUNT)
        if int.from_bytes(
            base[POINTER_TABLE_ROM_OFFSET + (index * 2):POINTER_TABLE_ROM_OFFSET + (index * 2) + 2],
            "little",
        )
        == old_pointer_cpu
    ]
    expected_indices = relocation["expected_pointer_indices"]
    assert isinstance(expected_indices, list)
    if actual_indices != expected_indices:
        raise ValueError("the preserved neighbour has unexpected pointer-table owners")

    old_record_length = int(relocation["preserved_record_length"])
    preserved_record = base[old_record_offset:old_record_offset + old_record_length]
    if len(preserved_record) != old_record_length or preserved_record[-1] != 0xFF:
        raise ValueError("the preserved neighbour record is not a complete terminated base-ROM record")

    relocated_rom_offset = CODE_CAVE_ROM_OFFSET + len(helper_code)
    relocated_cpu = CODE_CAVE_CPU + len(helper_code)
    relocated_end = relocated_rom_offset + len(preserved_record)
    if relocated_end > CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE:
        raise ValueError("the preserved neighbour does not fit in the approved code-cave tail")
    if base[relocated_rom_offset:relocated_end] != b"\xff" * len(preserved_record):
        raise ValueError("the intended code-cave relocation tail is not an untouched 0xFF run")

    expanded = bytearray(patched)
    expanded[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + len(encoded)] = encoded
    expanded[relocated_rom_offset:relocated_end] = preserved_record
    expanded[pointer_offset:pointer_offset + 2] = relocated_cpu.to_bytes(2, "little")

    dialogue_target = next(target for target in targets if target["kind"] == "dialogue_record")
    dialogue_target["length"] = len(encoded)
    dialogue_target["base_length"] = RECORD_LENGTH
    dialogue_target["expanded"] = True
    targets.append(
        {
            "kind": "relocated_neighbor_pointer",
            "rom_offset": pointer_offset,
            "length": 2,
            "pointer_index": relocation["preserved_pointer_index"],
            "original_cpu_address": f"0x{old_pointer_cpu:04X}",
            "relocated_cpu_address": f"0x{relocated_cpu:04X}",
        }
    )
    targets.append(
        {
            "kind": "relocated_neighbor_record",
            "rom_offset": relocated_rom_offset,
            "length": len(preserved_record),
            "original_rom_offset": old_record_offset,
            "cpu_address": f"0x{relocated_cpu:04X}",
            "pointer_index": relocation["preserved_pointer_index"],
        }
    )
    assert_scoped_changes(base, bytes(expanded), targets)
    return bytes(expanded), targets


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    lines = [
        "# Opening Dialogue Paired 16x16 Capacity Candidate",
        "",
        "Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_CAPACITY**",
        "",
        "This bounded candidate reads all code-pair and helper-range decisions from",
        "its scene catalog. Passing it proves only the named opening record and the",
        "captured screen context; it does not promote its compact wording to release text.",
        "",
        "## Scope",
        "",
        f"- Batch: `{source['batch_id']}`",
        f"- Pointer index: `{source['pointer_index']}`",
        f"- Record ROM offset: `{source['record_rom_offset']}`",
        f"- Record bytes: `{source['record_length']}` (base: `{source['base_record_length']}`).",
        f"- Candidate wording: {source['korean_text']}",
        f"- Unique glyphs: `{source['unique_glyph_count']}`; source slots: `{source['source_slot_count']}`.",
        f"- Helper range: `{source['helper_source_range']}`.",
        f"- English-reference source slots: `{source['english_reference_source_slot_count']}`.",
    ]
    relocation = source.get("relocation")
    if isinstance(relocation, dict):
        lines += [
            f"- Preserved neighbour pointer: `{relocation['pointer_index']}` at `{relocation['pointer_rom_offset']}`.",
            f"- Preserved neighbour record: `{relocation['original_record_rom_offset']}` -> `{relocation['relocated_rom_offset']}` / `{relocation['relocated_cpu_address']}`.",
        ]
    lines += [
        "",
        "## Result",
        "",
        f"- Base MD5: `{candidate['base_md5']}`",
        f"- Candidate MD5: `{candidate['patched_md5']}`",
        f"- Changed-byte spans: `{candidate['changed_span_count']}`; escaped bytes: `{candidate['escaped_byte_count']}`.",
        f"- IPS: `{candidate['ips_path']}`",
        f"- ROM: `{candidate['rom_path']}`",
        "",
        "Promotion requires the same bounded frame-883 capture, exact runtime",
        "record bytes, and a native screenshot with no visible background/UI damage.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--reference-ips", required=True, help="English reference IPS")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--font", help="Korean TrueType font path")
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
    ips_path = Path(args.reference_ips).expanduser()
    if not ips_path.is_file():
        raise FileNotFoundError(f"reference IPS not found: {ips_path}")

    config = validate_capacity_catalog(args.catalog)
    profile = config["profile"]
    assert isinstance(profile, dict)
    english_codes = profile["english_reference_source_codes"]
    pairs = profile["glyph_code_pairs"]
    source_codes = profile["source_codes"]
    start = profile["helper_start_code"]
    end_exclusive = profile["helper_end_code_exclusive"]
    assert isinstance(english_codes, tuple)
    assert isinstance(pairs, dict) and isinstance(source_codes, tuple)
    assert isinstance(start, int) and isinstance(end_exclusive, int)

    reference = validate_english_reference_source_slots(
        base, ips_path, source_codes=english_codes
    )
    font = default_square_font(args.font)
    glyph_tiles = build_square_glyph_tiles(font, pairs)
    patched, targets = apply_capacity_candidate(base, glyph_tiles, config)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_output = args.out_dir / f"{args.out_stem}.ips"
    rom_output = args.out_dir / f"{args.out_stem}.nes"
    write_ips(ips_output, records)
    rom_output.write_bytes(patched)
    write_square_preview(
        list(pairs), args.preview, font_path=font, target_pixels=15, threshold=100
    )

    changed = changed_spans(base, patched)
    relocation_payload = None
    relocation = config["relocation"]
    if isinstance(relocation, dict):
        relocation_target = next(
            target for target in targets if target["kind"] == "relocated_neighbor_record"
        )
        relocation_payload = {
            "pointer_index": relocation["preserved_pointer_index"],
            "pointer_rom_offset": f"0x{int(relocation['preserved_pointer_rom_offset']):05X}",
            "original_record_rom_offset": f"0x{int(relocation['preserved_record_rom_offset']):05X}",
            "original_record_length": relocation["preserved_record_length"],
            "relocated_rom_offset": f"0x{int(relocation_target['rom_offset']):05X}",
            "relocated_cpu_address": relocation_target["cpu_address"],
        }
    payload = {
        "status": "CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_CAPACITY",
        "source": {
            "batch_id": config["batch_id"],
            "base_md5": BASE_MD5,
            "pointer_index": POINTER_INDEX,
            "pointer_rom_offset": f"0x{POINTER_ROM_OFFSET:05X}",
            "record_rom_offset": f"0x{RECORD_ROM_OFFSET:05X}",
            "record_length": len(config["encoded"]),
            "base_record_length": config["base_record_length"],
            "catalog": config["catalog_path"],
            "catalog_sha256": config["catalog_sha256"],
            "korean_text": config["record"]["korean_text"],
            "font": str(font),
            "font_preview": str(args.preview),
            "chr_bank": CHR_BANK,
            "unique_glyph_count": len(pairs),
            "source_slot_count": len(source_codes),
            "helper_source_range": f"0x{start:02X}-0x{end_exclusive - 1:02X}",
            "english_reference_source_slot_count": len(english_codes),
            "english_reference_source_codes": [f"0x{code:02X}" for code in english_codes],
            "glyph_code_pairs": {
                glyph: [f"0x{left:02X}", f"0x{right:02X}"]
                for glyph, (left, right) in pairs.items()
            },
            "relocation": relocation_payload,
        },
        "english_reference_validation": reference,
        "candidate": {
            "base_md5": actual_md5,
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": str(ips_output),
            "rom_path": str(rom_output),
            "ips_record_count": len(records),
            "changed_span_count": len(changed),
            "changed_spans": [
                {"start": f"0x{start_offset:05X}", "end_exclusive": f"0x{end_offset:05X}"}
                for start_offset, end_offset in changed
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

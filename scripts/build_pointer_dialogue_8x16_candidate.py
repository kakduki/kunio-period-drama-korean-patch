#!/usr/bin/env python3
"""Build a bounded direct-8x16 Korean pointer-dialogue candidate.

This builder consumes the complete Korean draft and the English patch's
pointer catalog, but compiles only a declared small batch. It keeps the
English patch as a structural reference: Korean text, font pixels, and the
record relocation are produced locally. The candidate is intentionally a
soft-gate artifact, not a release patch.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_16x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
    _assert_scoped_changes,
    validate_english_reference_source_slots,
)
from build_opening_dialogue_proof import (
    BASE_MD5,
    CHR_BANK,
    physical_tile_for_code,
    resolve_base_rom,
    target_tile_offset,
)
from build_patch import make_records, write_ips
from compile_korean_scene_batch import CatalogError, parse_hex_byte
from korean_tile_font import find_korean_font, render_tall_tiles, write_tall_preview
from paired_dialogue_helper import build_record_scoped_paired_helper
from rom_utils import REPO_ROOT


BANK1_ROM_START = 0x04010
BANK1_CPU_START = 0x8000
POINTER_TABLE_ROM_OFFSET = 0x05DD4
POINTER_COUNT = 248
DEFAULT_POINTER_INDICES = (0, 1, 2)
DEFAULT_DRAFT = REPO_ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv"
DEFAULT_ENGLISH = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "pointer_dialogue_batch_000_002_8x16"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_000_002_8x16.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_000_002_8x16.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_000_002_8x16_font_preview.png"
DEFAULT_OUT_STEM = "kunio_period_drama_korean_pointer_dialogue_batch_000_002_8x16"
BOTTOM_TILE_DELTA = 0x20
CONTROL_BYTES = frozenset({0x00, 0xBB, 0xCA, 0xF8, 0xF9, 0xFF})
SOURCE_START = 0x81
SOURCE_END = 0xE0


def report_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def bank1_rom_to_cpu(rom_offset: int) -> int:
    return rom_offset - BANK1_ROM_START + BANK1_CPU_START


def bank1_cpu_to_rom(cpu_address: int) -> int:
    return cpu_address - BANK1_CPU_START + BANK1_ROM_START


def pointer_cpu(base: bytes, index: int) -> int:
    offset = POINTER_TABLE_ROM_OFFSET + index * 2
    return int.from_bytes(base[offset:offset + 2], "little")


def pointer_owners(base: bytes, cpu_address: int) -> list[int]:
    return [index for index in range(POINTER_COUNT) if pointer_cpu(base, index) == cpu_address]


def parse_pointer_indices(value: str) -> tuple[int, ...]:
    try:
        indices = tuple(int(item.strip(), 10) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise CatalogError("pointer indices must be comma-separated decimal integers") from exc
    if not indices or len(set(indices)) != len(indices):
        raise CatalogError("pointer indices must be non-empty and unique")
    if any(not 0 <= index < POINTER_COUNT for index in indices):
        raise CatalogError("pointer index is outside 0..247")
    if indices != tuple(sorted(indices)):
        raise CatalogError("pointer indices must be sorted")
    return indices


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_draft(path: Path) -> dict[int, dict[str, str]]:
    rows = load_tsv(path)
    if len(rows) != POINTER_COUNT:
        raise CatalogError(f"expected {POINTER_COUNT} Korean draft rows, found {len(rows)}")
    result: dict[int, dict[str, str]] = {}
    for row in rows:
        index = int(row["pointer_index"])
        if index in result:
            raise CatalogError(f"duplicate Korean draft pointer {index}")
        if not row["korean_text"].strip() and not row["translation_status"].startswith("excluded"):
            raise CatalogError(f"pointer {index} has an empty Korean draft")
        result[index] = row
    if set(result) != set(range(POINTER_COUNT)):
        raise CatalogError("Korean draft does not contain every pointer index")
    return result


def load_english_rows(path: Path) -> dict[int, dict[str, str]]:
    rows = [row for row in load_tsv(path) if row.get("record_kind") == "pointer_pair"]
    if len(rows) != POINTER_COUNT:
        raise CatalogError(f"expected {POINTER_COUNT} English pointer rows, found {len(rows)}")
    result = {int(row["pointer_index"]): row for row in rows}
    if set(result) != set(range(POINTER_COUNT)):
        raise CatalogError("English pointer catalog does not contain every pointer index")
    return result


def encode_draft(text: str, glyph_codes: dict[str, int]) -> bytes:
    encoded = bytearray((0xF0, 0xBB, 0x00))
    for character in text:
        if character == " ":
            encoded.append(0x00)
        else:
            try:
                encoded.append(glyph_codes[character])
            except KeyError as exc:
                raise CatalogError(f"unallocated Korean character {character!r}") from exc
    encoded.extend((0xCA, 0xFF))
    return bytes(encoded)


def allocate_glyph_codes(rows: dict[int, dict[str, str]], indices: tuple[int, ...]) -> dict[str, int]:
    characters: list[str] = []
    for index in indices:
        for character in rows[index]["korean_text"]:
            if character != " " and character not in characters:
                characters.append(character)
    if len(characters) > SOURCE_END - SOURCE_START:
        raise CatalogError(
            f"batch needs {len(characters)} source glyphs, but direct range has "
            f"{SOURCE_END - SOURCE_START} slots"
        )
    codes = {character: SOURCE_START + offset for offset, character in enumerate(characters)}
    if any(code in CONTROL_BYTES or code + BOTTOM_TILE_DELTA > 0xFF for code in codes.values()):
        raise CatalogError("allocated glyph source collides with a renderer control or bottom tile")
    return codes


def build_config(
    base: bytes,
    draft_path: Path,
    english_path: Path,
    indices: tuple[int, ...],
) -> dict[str, object]:
    draft = load_draft(draft_path)
    english = load_english_rows(english_path)
    glyph_codes = allocate_glyph_codes(draft, indices)
    records: list[dict[str, object]] = []
    for index in indices:
        english_row = english[index]
        if draft[index]["translation_status"].startswith("excluded"):
            raise CatalogError(f"pointer {index} is excluded from a build batch")
        original_offset = int(english_row["jp_rom_offset"], 16)
        original_bytes = bytes.fromhex(english_row["jp_raw_bytes"])
        if pointer_cpu(base, index) != int(english_row["jp_pointer_cpu"], 16):
            raise CatalogError(f"pointer {index} disagrees with the English catalog")
        if base[original_offset:original_offset + len(original_bytes)] != original_bytes:
            raise CatalogError(f"pointer {index} source bytes disagree with the base ROM")
        records.append(
            {
                "pointer_index": index,
                "pointer_rom_offset": POINTER_TABLE_ROM_OFFSET + index * 2,
                "original_record_rom_offset": original_offset,
                "original_length": len(original_bytes),
                "old_pointer_cpu": pointer_cpu(base, index),
                "korean_text": draft[index]["korean_text"],
                "translation_status": draft[index]["translation_status"],
                "english_reference": english_row["en_text"],
                "encoded": None,
            }
        )

    pack_offset = min(int(record["original_record_rom_offset"]) for record in records)
    next_unselected = min(
        (
            int(row["jp_rom_offset"], 16)
            for index, row in english.items()
            if index not in indices and int(row["jp_rom_offset"], 16) > pack_offset
        ),
        default=0x08010,
    )
    cursor = pack_offset
    for record in records:
        encoded = encode_draft(str(record["korean_text"]), glyph_codes)
        if cursor + len(encoded) > next_unselected:
            raise CatalogError(
                f"packed batch reaches 0x{cursor + len(encoded):05X}, "
                f"past protected next record 0x{next_unselected:05X}"
            )
        record["record_rom_offset"] = cursor
        record["new_pointer_cpu"] = bank1_rom_to_cpu(cursor)
        record["encoded"] = encoded
        cursor += len(encoded)

    high_bytes = {int(record["new_pointer_cpu"]) >> 8 for record in records}
    if len(high_bytes) != 1:
        raise CatalogError("record-scoped helper requires one CPU high byte")
    for record in records:
        old_cpu = int(record["old_pointer_cpu"])
        new_cpu = int(record["new_pointer_cpu"])
        if old_cpu != new_cpu and pointer_owners(base, old_cpu) != [int(record["pointer_index"])]:
            raise CatalogError(f"pointer {record['pointer_index']} has unexpected old owners")
        existing = pointer_owners(base, new_cpu)
        if existing and existing != [int(record["pointer_index"])]:
            raise CatalogError(f"pointer {record['pointer_index']} collides at new CPU address")
    return {
        "draft_path": draft_path,
        "english_path": english_path,
        "indices": indices,
        "batch_id": f"pointer_dialogue_batch_{indices[0]:03d}_{indices[-1]:03d}_8x16",
        "draft_sha256": hashlib.sha256(draft_path.read_bytes()).hexdigest(),
        "english_sha256": hashlib.sha256(english_path.read_bytes()).hexdigest(),
        "glyph_codes": glyph_codes,
        "records": records,
        "pack_start": pack_offset,
        "pack_end": cursor,
        "protected_next_record": next_unselected,
    }


def apply_tall_renderer_assets(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes]],
    glyph_codes: dict[str, int],
    helper_code: bytes,
    marker_helper_cpu: int,
    source_end: int,
) -> tuple[bytes, list[dict[str, object]]]:
    if base[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] != RENDER_ENTRY_ORIGINAL:
        raise ValueError("renderer entry bytes do not match the base ROM")
    if base[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] != RENDER_MARKER_ORIGINAL:
        raise ValueError("renderer marker bytes do not match the base ROM")
    cave_end = CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE
    if base[CODE_CAVE_ROM_OFFSET:cave_end] != b"\xff" * CODE_CAVE_SIZE:
        raise ValueError("renderer code cave is not an untouched 0xFF run")
    if len(helper_code) > CODE_CAVE_SIZE:
        raise ValueError("renderer helper does not fit the approved code cave")

    layout = parse_ines_layout(base)
    patched = bytearray(base)
    targets: list[dict[str, object]] = []
    for character, code in glyph_codes.items():
        tiles = glyph_tiles.get(character)
        if tiles is None or len(tiles) != 2 or any(len(tile) != 16 for tile in tiles):
            raise ValueError(f"missing direct 8x16 glyph tiles for {character!r}")
        for kind, tile_code, tile in (
            ("font_tile_top", code, tiles[0]),
            ("font_tile_bottom", code + BOTTOM_TILE_DELTA, tiles[1]),
        ):
            offset = target_tile_offset(layout, tile_code)
            patched[offset:offset + 16] = tile
            targets.append(
                {
                    "kind": kind,
                    "rom_offset": offset,
                    "length": 16,
                    "character": character,
                    "code": f"0x{tile_code:02X}",
                    "physical_tile": f"0x{physical_tile_for_code(tile_code):03X}",
                }
            )

    entry_hook = bytes((0x4C, CODE_CAVE_CPU & 0xFF, CODE_CAVE_CPU >> 8))
    marker_hook = bytes((0x4C, marker_helper_cpu & 0xFF, marker_helper_cpu >> 8))
    patched[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + 3] = entry_hook
    patched[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + 3] = marker_hook
    patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + len(helper_code)] = helper_code
    targets.extend(
        (
            {
                "kind": "renderer_entry_hook",
                "rom_offset": RENDER_ENTRY_ROM_OFFSET,
                "length": 3,
                "cpu_address": "0x955F",
            },
            {
                "kind": "renderer_marker_hook",
                "rom_offset": RENDER_MARKER_ROM_OFFSET,
                "length": 3,
                "cpu_address": "0x9576",
                "helper_cpu_address": f"0x{marker_helper_cpu:04X}",
            },
            {
                "kind": "renderer_helper",
                "rom_offset": CODE_CAVE_ROM_OFFSET,
                "length": len(helper_code),
                "cpu_address": f"0x{CODE_CAVE_CPU:04X}",
                "source_range": f"0x{SOURCE_START:02X}-0x{source_end - 1:02X}",
            },
        )
    )
    _assert_scoped_changes(base, bytes(patched), targets, label="direct 8x16 pointer candidate")
    return bytes(patched), targets


def apply_candidate(base: bytes, config: dict[str, object], glyph_tiles: dict[str, tuple[bytes, bytes]]) -> tuple[bytes, list[dict[str, object]], object]:
    records = config["records"]
    glyph_codes = config["glyph_codes"]
    assert isinstance(records, list) and isinstance(glyph_codes, dict)
    source_ranges = ((SOURCE_START, SOURCE_START + len(glyph_codes)),)
    helper = build_record_scoped_paired_helper(
        record_cpu_addresses=tuple(int(record["new_pointer_cpu"]) for record in records),
        source_ranges=source_ranges,
        entry_cpu=CODE_CAVE_CPU,
        max_size=CODE_CAVE_SIZE,
    )
    patched, targets = apply_tall_renderer_assets(
        base,
        glyph_tiles,
        glyph_codes,
        helper.code,
        helper.marker_cpu,
        SOURCE_START + len(glyph_codes),
    )
    patched_bytes = bytearray(patched)
    for record in records:
        offset = int(record["record_rom_offset"])
        encoded = record["encoded"]
        assert isinstance(encoded, bytes)
        patched_bytes[offset:offset + len(encoded)] = encoded
        targets.append(
            {
                "kind": "dialogue_record",
                "rom_offset": offset,
                "length": len(encoded),
                "pointer_index": record["pointer_index"],
                "cpu_address": f"0x{int(record['new_pointer_cpu']):04X}",
            }
        )
    for record in records:
        old_cpu = int(record["old_pointer_cpu"])
        new_cpu = int(record["new_pointer_cpu"])
        if old_cpu == new_cpu:
            continue
        offset = int(record["pointer_rom_offset"])
        patched_bytes[offset:offset + 2] = new_cpu.to_bytes(2, "little")
        targets.append(
            {
                "kind": "dialogue_pointer",
                "rom_offset": offset,
                "length": 2,
                "pointer_index": record["pointer_index"],
                "original_cpu_address": f"0x{old_cpu:04X}",
                "new_cpu_address": f"0x{new_cpu:04X}",
            }
        )
    _assert_scoped_changes(base, bytes(patched_bytes), targets, label="direct 8x16 pointer candidate")
    return bytes(patched_bytes), targets, helper


def default_font(candidate: str | Path | None) -> Path:
    if candidate is not None:
        return find_korean_font(candidate)
    bold = Path(r"C:\Windows\Fonts\malgunbd.ttf")
    return find_korean_font(bold if bold.is_file() else None)


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    records = source["records"]
    lines = [
        "# Pointer Dialogue Batch 000-002 Direct 8x16 Candidate",
        "",
        "Status: **CANDIDATE_BUILT_RUNTIME_UNKNOWN**",
        "",
        "This is a soft-gate candidate, not a release patch. It compiles only",
        "pointers 0, 1, and 2 from the Korean semantic draft, using the English",
        "patch for pointer ownership and record placement structure.",
        "",
        "## Scope",
        "",
        f"- Batch: `{source['batch_id']}`; pointer indices: `{source['pointer_indices']}`.",
        f"- Direct 8x16 glyphs: `{source['glyph_count']}` in source range `{source['source_range']}`.",
        f"- Packed record window: `{source['pack_start']}` to `{source['pack_end']}`; protected next record: `{source['protected_next_record']}`.",
        "- Each candidate record uses the conservative `F0 BB 00 ... CA FF` shape.",
        "- p0 has multiple source messages in the original record; this first candidate compacts its draft to one message and therefore remains structurally risky.",
        "",
        "| pointer | old CPU | new CPU | encoded bytes | Korean draft |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for record in records:
        lines.append(
            f"| {record['pointer_index']} | `{record['old_pointer_cpu']}` | "
            f"`{record['new_pointer_cpu']}` | {record['encoded_length']} | {record['korean_text']} |"
        )
    lines += [
        "",
        "## Candidate",
        "",
        f"- Base MD5: `{candidate['base_md5']}`.",
        f"- Candidate MD5: `{candidate['patched_md5']}`.",
        f"- ROM: `{candidate['rom_path']}`.",
        f"- IPS: `{candidate['ips_path']}`.",
        f"- Changed spans: `{candidate['changed_span_count']}`; escaped bytes: `{candidate['escaped_byte_count']}`.",
        "",
        "## Runtime Gate",
        "",
        "- Verdict: **UNKNOWN** until a bounded save-state or route reaches one of these non-opening pointers.",
        "- Boot success alone does not promote this candidate, and the opening-loop symptom is not treated as dialogue evidence.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--pointer-indices", default=",".join(str(index) for index in DEFAULT_POINTER_INDICES))
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--english", type=Path, default=DEFAULT_ENGLISH)
    parser.add_argument("--reference-ips", type=Path, default=REPO_ROOT / "tools" / "reference" / "TSe-v10.ips")
    parser.add_argument("--font", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--out-stem", default=DEFAULT_OUT_STEM)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    args = parser.parse_args()

    indices = parse_pointer_indices(args.pointer_indices)
    rom_path = resolve_base_rom(args.rom)
    base = rom_path.read_bytes()
    actual_md5 = hashlib.md5(base).hexdigest()
    if actual_md5 != BASE_MD5:
        raise ValueError(f"unsupported base ROM MD5: {actual_md5}")
    config = build_config(base, args.draft, args.english, indices)
    font = default_font(args.font)
    glyph_codes = config["glyph_codes"]
    assert isinstance(glyph_codes, dict)
    glyph_tiles = {character: render_tall_tiles(character, font_path=font, threshold=92) for character in glyph_codes}
    patched, targets, helper = apply_candidate(base, config, glyph_tiles)
    reference = validate_english_reference_source_slots(
        base,
        args.reference_ips,
        source_codes=tuple(glyph_codes.values()),
    )
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{args.out_stem}.ips"
    rom_path_out = args.out_dir / f"{args.out_stem}.nes"
    write_ips(ips_path, records)
    rom_path_out.write_bytes(patched)
    write_tall_preview(list(glyph_codes), args.preview, font_path=font, threshold=92)

    source_records = []
    for record in config["records"]:
        source_records.append(
            {
                "pointer_index": record["pointer_index"],
                "old_pointer_cpu": f"0x{int(record['old_pointer_cpu']):04X}",
                "new_pointer_cpu": f"0x{int(record['new_pointer_cpu']):04X}",
                "original_record_rom_offset": f"0x{int(record['original_record_rom_offset']):05X}",
                "record_rom_offset": f"0x{int(record['record_rom_offset']):05X}",
                "original_length": record["original_length"],
                "encoded_length": len(record["encoded"]),
                "korean_text": record["korean_text"],
                "translation_status": record["translation_status"],
                "english_reference": record["english_reference"],
            }
        )
    payload = {
        "status": "CANDIDATE_BUILT_RUNTIME_UNKNOWN",
        "source": {
            "base_md5": BASE_MD5,
            "batch_id": config["batch_id"],
            "pointer_indices": list(indices),
            "draft": report_path(args.draft),
            "draft_sha256": config["draft_sha256"],
            "english_catalog": report_path(args.english),
            "english_sha256": config["english_sha256"],
            "reference_ips": report_path(args.reference_ips),
            "reference_validation": reference,
            "font": str(font),
            "font_preview": report_path(args.preview),
            "glyph_codes": {character: f"0x{code:02X}" for character, code in glyph_codes.items()},
            "glyph_count": len(glyph_codes),
            "source_range": f"0x{SOURCE_START:02X}-0x{SOURCE_START + len(glyph_codes) - 1:02X}",
            "helper_length": len(helper.code),
            "helper_cpu": f"0x{helper.entry_cpu:04X}",
            "marker_helper_cpu": f"0x{helper.marker_cpu:04X}",
            "chr_bank": CHR_BANK,
            "pack_start": f"0x{int(config['pack_start']):05X}",
            "pack_end": f"0x{int(config['pack_end']):05X}",
            "protected_next_record": f"0x{int(config['protected_next_record']):05X}",
            "records": source_records,
        },
        "candidate": {
            "base_md5": actual_md5,
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "rom_path": report_path(rom_path_out),
            "ips_path": report_path(ips_path),
            "ips_record_count": len(records),
            "changed_span_count": len(make_records(base, patched)),
            "escaped_byte_count": 0,
            "targets": targets,
        },
        "runtime_gate": {
            "verdict": "UNKNOWN",
            "reason": "No bounded early-boss route or save-state entry is proven yet.",
            "boot": "not_run",
            "pointer_0_visible": "unknown",
            "pointer_1_visible": "unknown",
            "pointer_2_visible": "unknown",
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

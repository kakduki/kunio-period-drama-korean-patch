#!/usr/bin/env python3
"""Build a bounded 16x16 Korean-font proof for one real opening dialogue.

The verified dialogue renderer already emits one vertical 8x16 tile pair for
each source byte. This proof uses two adjacent, already-proven source slots
per Korean syllable: the first writes the left 8x16 half and the second writes
the right half. It deliberately avoids a new VRAM queue format and keeps the
existing target-record gate from the 8x16 proof.

This is a renderer/font experiment, not a release translation. Its compact
wording keeps the proof inside the 17 source slots that have native-screen
evidence, while a later text pipeline must solve full glyph capacity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ines_layout, parse_ips
from build_opening_dialogue_8x16_proof import (
    BOTTOM_TILE_DELTA,
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    ENTRY_HOOK,
    HELPER_CODE,
    MARKER_HOOK,
    RENDER_ENTRY_CPU,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_CPU,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
)
from build_opening_dialogue_proof import (
    BASE_MD5,
    CHR_BANK,
    KOREAN_GLYPH_CODES,
    ORIGINAL_RECORD,
    POINTER_INDEX,
    POINTER_ROM_OFFSET,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    physical_tile_for_code,
    resolve_base_rom,
    target_tile_offset,
)
from build_patch import make_records, write_ips
from compile_korean_scene_batch import CatalogError, load_catalog, parse_hex_byte, parse_hex_bytes
from korean_tile_font import find_korean_font, render_square_tiles, write_square_preview
from rom_utils import REPO_ROOT


DEFAULT_CATALOG = REPO_ROOT / "text_data" / "korean_scene_batches" / "opening_ptr_182_16x16.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_dialogue_16x16_proof"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_16x16_proof.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_16x16_proof.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_16x16_font_preview.png"
OUT_STEM = "kunio_period_drama_korean_opening_dialogue_16x16_proof"

# Left and right source bytes are rendered by the already-proven vertical
# 8x16 route. 0x8A and 0x8B remain excluded because the original renderer has
# special branches for them. Every pair is contained in the existing safe set.
PAIR_GLYPH_CODES: dict[str, tuple[int, int]] = {
    "\uCFE0": (0x81, 0x8C),
    "\uB2C8": (0x82, 0x8D),
    "\uB9C8": (0x83, 0x8E),
    "\uC0AC": (0x84, 0x8F),
    "\uC5B4": (0x85, 0x90),
    "\uC11C": (0x86, 0x91),
    "\uBD84": (0x87, 0x92),
    "\uC870": (0x88, 0x93),
}
PAIR_SOURCE_CODES = tuple(code for pair in PAIR_GLYPH_CODES.values() for code in pair)
PROOF_RECORD = bytes.fromhex(
    "81 8C 82 8D 83 8E 84 8F BB 00 85 90 86 91 CA F8 "
    "87 92 88 93 CA 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 FF"
)
SOURCE_RANGE_PATTERN = bytes.fromhex("C9 81 90 0D C9 94 B0 09")


def default_square_font(candidate: str | Path | None) -> Path:
    if candidate is not None:
        return find_korean_font(candidate)
    bold = Path(r"C:\Windows\Fonts\malgunbd.ttf")
    if bold.is_file():
        return bold
    return find_korean_font()


def encode_pair_tokens(
    tokens: object,
    glyph_code_pairs: dict[str, tuple[int, int]] = PAIR_GLYPH_CODES,
) -> tuple[bytes, list[str]]:
    """Encode explicit control bytes plus known two-byte Korean glyph pairs."""

    if not isinstance(tokens, list) or not tokens:
        raise CatalogError("16x16 proof tokens must be a non-empty list")
    encoded = bytearray()
    glyphs: list[str] = []
    for index, token in enumerate(tokens):
        if not isinstance(token, dict):
            raise CatalogError(f"16x16 proof token {index} must be an object")
        has_pair = "glyph_pair" in token
        has_byte = "byte" in token
        if has_pair == has_byte:
            raise CatalogError(
                f"16x16 proof token {index} must contain exactly one of glyph_pair or byte"
            )
        if has_pair:
            glyph = token["glyph_pair"]
            if not isinstance(glyph, str) or len(glyph) != 1:
                raise CatalogError(f"16x16 proof token {index} glyph_pair must be one character")
            pair = glyph_code_pairs.get(glyph)
            if pair is None:
                raise CatalogError(f"16x16 proof token {index} has no approved pair: {glyph!r}")
            encoded.extend(pair)
            if glyph not in glyphs:
                glyphs.append(glyph)
        else:
            encoded.append(parse_hex_byte(token["byte"]))
    return bytes(encoded), glyphs


def validate_opening_16x16_catalog(catalog_path: Path) -> dict[str, object]:
    """Load the scene-owned proof data without granting broader font capacity."""

    catalog = load_catalog(catalog_path)
    if catalog.get("batch_id") != "opening_ptr_182_16x16_proof":
        raise CatalogError("16x16 proof catalog has an unexpected batch id")
    if catalog.get("renderer_profile") != "paired_8x16_cells_for_16x16_korean":
        raise CatalogError("16x16 proof catalog has an unexpected renderer profile")
    records = catalog["records"]
    assert isinstance(records, list)
    if len(records) != 1 or not isinstance(records[0], dict):
        raise CatalogError("16x16 proof catalog must contain exactly one record")
    record = records[0]
    if (
        record.get("id") != "PTR-182-16X16"
        or record.get("pointer_index") != POINTER_INDEX
        or record.get("pointer_rom_offset") != f"0x{POINTER_ROM_OFFSET:05X}"
        or record.get("record_rom_offset") != f"0x{RECORD_ROM_OFFSET:05X}"
        or record.get("expected_length") != RECORD_LENGTH
    ):
        raise CatalogError("16x16 proof catalog does not identify the verified opening record")
    original = parse_hex_bytes(
        record.get("expected_original_bytes"), field="16x16 proof expected_original_bytes"
    )
    if original != ORIGINAL_RECORD:
        raise CatalogError("16x16 proof catalog source bytes diverge from the verified base ROM")
    encoded, glyphs = encode_pair_tokens(record.get("tokens"))
    if encoded != PROOF_RECORD:
        raise CatalogError("16x16 proof catalog bytes diverge from the approved paired proof")
    if len(encoded) != RECORD_LENGTH or encoded[-1] != 0xFF:
        raise CatalogError("16x16 proof record length or terminator is invalid")
    if glyphs != list(PAIR_GLYPH_CODES):
        raise CatalogError("16x16 proof glyph order does not match the approved tile allocation")
    source = catalog_path.read_bytes()
    return {
        "catalog_path": str(catalog_path),
        "catalog_sha256": hashlib.sha256(source).hexdigest(),
        "record": record,
        "encoded": encoded,
        "glyphs": glyphs,
    }


def build_square_glyph_tiles(
    font_path: str | Path | None,
    glyph_code_pairs: dict[str, tuple[int, int]] = PAIR_GLYPH_CODES,
) -> dict[str, tuple[bytes, bytes, bytes, bytes]]:
    return {
        glyph: render_square_tiles(glyph, font_path=font_path, target_pixels=15, threshold=100)
        for glyph in glyph_code_pairs
    }


def source_codes_for_pairs(glyph_code_pairs: dict[str, tuple[int, int]]) -> tuple[int, ...]:
    return tuple(code for pair in glyph_code_pairs.values() for code in pair)


def helper_code_for_range(
    *,
    start_code: int = 0x81,
    end_code_exclusive: int = 0x94,
) -> bytes:
    """Retarget the bounded helper to one contiguous source-code range.

    Both range checks live in the same 0xFF code cave as the original proof.
    This changes only comparison immediates; the helper length and branch
    layout remain unchanged. Callers must still keep special control bytes out
    of their allocated range.
    """

    if not 0x80 <= start_code < end_code_exclusive <= 0xE0:
        raise ValueError("helper source-code range must fit below parser control bytes")
    replacement = bytes((0xC9, start_code, 0x90, 0x0D, 0xC9, end_code_exclusive, 0xB0, 0x09))
    if HELPER_CODE.count(SOURCE_RANGE_PATTERN) != 2:
        raise AssertionError("unexpected bounded helper range-check layout")
    helper = HELPER_CODE.replace(SOURCE_RANGE_PATTERN, replacement)
    if len(helper) != len(HELPER_CODE):
        raise AssertionError("retargeted helper changed length")
    return helper


def add_target(
    targets: list[dict[str, object]],
    *,
    kind: str,
    rom_offset: int,
    length: int,
    **extra: object,
) -> None:
    targets.append({"kind": kind, "rom_offset": rom_offset, "length": length, **extra})


def apply_paired_opening_candidate(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
    *,
    proof_record: bytes,
    glyph_code_pairs: dict[str, tuple[int, int]],
    helper_code: bytes,
    helper_start_code: int,
    helper_end_code_exclusive: int,
) -> tuple[bytes, list[dict[str, object]]]:
    """Apply one bounded paired-cell record and a parameterized helper range."""

    if len(proof_record) != RECORD_LENGTH:
        raise AssertionError("paired 16x16 record length invariant failed")
    if base[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] != ORIGINAL_RECORD:
        raise ValueError("opening source record does not match the verified base bytes")
    if base[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] != RENDER_ENTRY_ORIGINAL:
        raise ValueError("renderer entry bytes do not match the verified base ROM")
    if base[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] != RENDER_MARKER_ORIGINAL:
        raise ValueError("renderer marker bytes do not match the verified base ROM")
    cave_end = CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE
    if base[CODE_CAVE_ROM_OFFSET:cave_end] != b"\xff" * CODE_CAVE_SIZE:
        raise ValueError("the paired-cell renderer cave is not an untouched 0xFF run")
    if len(helper_code) > CODE_CAVE_SIZE:
        raise AssertionError("paired-cell renderer helper does not fit the approved cave")
    source_codes = source_codes_for_pairs(glyph_code_pairs)
    if not source_codes:
        raise ValueError("paired 16x16 candidate needs at least one glyph pair")
    if len(set(source_codes)) != len(source_codes):
        raise AssertionError("paired 16x16 candidate reuses a source slot across tile halves")
    if not all(helper_start_code <= code < helper_end_code_exclusive for code in source_codes):
        raise AssertionError("paired 16x16 source slot is outside the helper range")
    if not all(code + BOTTOM_TILE_DELTA <= 0xFF for code in source_codes):
        raise AssertionError("paired 16x16 source slot has no in-bank bottom tile")
    tile_codes = set(source_codes) | {code + BOTTOM_TILE_DELTA for code in source_codes}
    if len(tile_codes) != len(source_codes) * 2:
        raise AssertionError("paired 16x16 source and bottom tile slots collide")

    layout = parse_ines_layout(base)
    patched = bytearray(base)
    targets: list[dict[str, object]] = []
    patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = proof_record
    add_target(
        targets,
        kind="dialogue_record",
        rom_offset=RECORD_ROM_OFFSET,
        length=RECORD_LENGTH,
        pointer_rom_offset=POINTER_ROM_OFFSET,
    )

    for glyph, (left_code, right_code) in glyph_code_pairs.items():
        tiles = glyph_tiles.get(glyph)
        if tiles is None or len(tiles) != 4 or any(len(tile) != 16 for tile in tiles):
            raise ValueError(f"missing 16x16 tile quartet for {glyph!r}")
        placements = (
            ("font_tile_top_left", left_code, tiles[0]),
            ("font_tile_top_right", right_code, tiles[1]),
            ("font_tile_bottom_left", left_code + BOTTOM_TILE_DELTA, tiles[2]),
            ("font_tile_bottom_right", right_code + BOTTOM_TILE_DELTA, tiles[3]),
        )
        for kind, code, tile in placements:
            offset = target_tile_offset(layout, code)
            patched[offset:offset + len(tile)] = tile
            add_target(
                targets,
                kind=kind,
                rom_offset=offset,
                length=len(tile),
                glyph=glyph,
                code=f"0x{code:02X}",
                physical_tile=f"0x{physical_tile_for_code(code):03X}",
            )

    patched[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(ENTRY_HOOK)] = ENTRY_HOOK
    add_target(
        targets,
        kind="renderer_entry_hook",
        rom_offset=RENDER_ENTRY_ROM_OFFSET,
        length=len(ENTRY_HOOK),
        cpu_address=f"0x{RENDER_ENTRY_CPU:04X}",
    )
    patched[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(MARKER_HOOK)] = MARKER_HOOK
    add_target(
        targets,
        kind="renderer_marker_hook",
        rom_offset=RENDER_MARKER_ROM_OFFSET,
        length=len(MARKER_HOOK),
        cpu_address=f"0x{RENDER_MARKER_CPU:04X}",
    )
    patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + len(helper_code)] = helper_code
    add_target(
        targets,
        kind="renderer_helper",
        rom_offset=CODE_CAVE_ROM_OFFSET,
        length=len(helper_code),
        cpu_address=f"0x{CODE_CAVE_CPU:04X}",
    )

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
        raise AssertionError(f"paired 16x16 candidate changed {len(escaped)} byte(s) outside its allowlist")
    return bytes(patched), targets


def apply_opening_16x16_proof(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
) -> tuple[bytes, list[dict[str, object]]]:
    """Apply the original eight-glyph proof through the generic bounded path."""

    safe_codes = set(KOREAN_GLYPH_CODES.values())
    if not set(PAIR_SOURCE_CODES) <= safe_codes:
        raise AssertionError("16x16 proof uses a source code without 8x16 runtime evidence")
    return apply_paired_opening_candidate(
        base,
        glyph_tiles,
        proof_record=PROOF_RECORD,
        glyph_code_pairs=PAIR_GLYPH_CODES,
        helper_code=HELPER_CODE,
        helper_start_code=0x81,
        helper_end_code_exclusive=0x94,
    )


def changed_spans(original: bytes, patched: bytes) -> list[tuple[int, int]]:
    offsets = [index for index, pair in enumerate(zip(original, patched)) if pair[0] != pair[1]]
    if not offsets:
        return []
    spans: list[tuple[int, int]] = []
    start = previous = offsets[0]
    for offset in offsets[1:]:
        if offset != previous + 1:
            spans.append((start, previous + 1))
            start = offset
        previous = offset
    spans.append((start, previous + 1))
    return spans


def validate_english_reference_source_slots(
    base: bytes,
    ips_path: Path,
    *,
    source_codes: tuple[int, ...] = PAIR_SOURCE_CODES,
) -> dict[str, object]:
    """Confirm English reference ownership of the source half slots only.

    The bottom half slots are selected from the native 8x16 proof, not copied
    from English. This keeps the English patch a structural reference instead
    of a source of Korean font pixels.
    """

    records, truncate_size = parse_ips(ips_path.read_bytes())
    reference = apply_records(base, records, truncate_size)
    layout = parse_ines_layout(base)
    slots = []
    for code in sorted(source_codes):
        offset = target_tile_offset(layout, code)
        if base[offset:offset + 16] == reference[offset:offset + 16]:
            raise ValueError(f"English reference did not change source slot 0x{code:02X}")
        slots.append(
            {
                "code": f"0x{code:02X}",
                "physical_tile": f"0x{physical_tile_for_code(code):03X}",
                "rom_offset": f"0x{offset:05X}",
            }
        )
    return {
        "ips_sha256": hashlib.sha256(ips_path.read_bytes()).hexdigest(),
        "validated_source_slots": slots,
        "note": "Only source-slot ownership is validated from English. Korean pixels are generated locally.",
    }


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    return "\n".join(
        [
            "# Opening Dialogue 16x16 Korean Proof Candidate",
            "",
            "Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_FONT_16X16**",
            "",
            "This proof does not invent a new dialogue queue. Each Korean syllable is",
            "a pair of adjacent, existing 8x16 dialogue cells, forming one native 16x16",
            "glyph. The underlying 8x16 target-record gate has already been captured;",
            "this candidate still needs its own bounded native-screen review.",
            "",
            "## Scope",
            "",
            f"- Pointer index: `{source['pointer_index']}`",
            f"- Record ROM offset: `{source['record_rom_offset']}`",
            f"- Proof wording: {source['korean_text']}",
            f"- Unique proof glyphs: `{source['unique_glyph_count']}`; source slots: `{source['source_slot_count']}`.",
            "- This compact wording is a font proof only, not the final release translation.",
            "",
            "## Bounds",
            "",
            f"- Renderer entry hook: `{source['renderer_entry_rom_offset']}` -> `{source['renderer_entry_cpu']}`",
            f"- Renderer marker hook: `{source['renderer_marker_rom_offset']}` -> `{source['renderer_marker_cpu']}`",
            f"- Same-page code cave: `{source['code_cave_rom_offset']}` -> `{source['code_cave_cpu']}`",
            "- The hook executes only for record `$B1A6` and safe source codes `0x81-0x93`.",
            "- The English reference validates source-slot structure only; no English pixels or text are copied.",
            "",
            "## Result",
            "",
            f"- Base MD5: `{candidate['base_md5']}`",
            f"- Candidate MD5: `{candidate['patched_md5']}`",
            f"- Changed-byte spans: `{candidate['changed_span_count']}`; escaped bytes: `{candidate['escaped_byte_count']}`.",
            f"- IPS: `{candidate['ips_path']}`",
            f"- ROM: `{candidate['rom_path']}`",
            "",
            "The only runtime check is the known opening route, capped at one capture",
            "frame. It stops immediately after the capture rather than entering gameplay.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--reference-ips", required=True, help="English reference IPS")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--font", help="Korean TrueType font path")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
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

    catalog = validate_opening_16x16_catalog(args.catalog)
    reference = validate_english_reference_source_slots(base, ips_path)
    font = default_square_font(args.font)
    glyph_tiles = build_square_glyph_tiles(font)
    patched, targets = apply_opening_16x16_proof(base, glyph_tiles)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_output = args.out_dir / f"{OUT_STEM}.ips"
    rom_output = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_output, records)
    rom_output.write_bytes(patched)
    write_square_preview(list(PAIR_GLYPH_CODES), args.preview, font_path=font, target_pixels=15, threshold=100)

    changed = changed_spans(base, patched)
    payload = {
        "status": "CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_FONT_16X16",
        "source": {
            "base_md5": BASE_MD5,
            "pointer_index": POINTER_INDEX,
            "pointer_rom_offset": f"0x{POINTER_ROM_OFFSET:05X}",
            "record_rom_offset": f"0x{RECORD_ROM_OFFSET:05X}",
            "record_length": RECORD_LENGTH,
            "catalog": catalog["catalog_path"],
            "catalog_sha256": catalog["catalog_sha256"],
            "korean_text": catalog["record"]["korean_text"],
            "font": str(font),
            "font_preview": str(args.preview),
            "renderer_entry_rom_offset": f"0x{RENDER_ENTRY_ROM_OFFSET:05X}",
            "renderer_entry_cpu": f"0x{RENDER_ENTRY_CPU:04X}",
            "renderer_marker_rom_offset": f"0x{RENDER_MARKER_ROM_OFFSET:05X}",
            "renderer_marker_cpu": f"0x{RENDER_MARKER_CPU:04X}",
            "code_cave_rom_offset": f"0x{CODE_CAVE_ROM_OFFSET:05X}",
            "code_cave_cpu": f"0x{CODE_CAVE_CPU:04X}",
            "helper_length": len(HELPER_CODE),
            "chr_bank": CHR_BANK,
            "unique_glyph_count": len(PAIR_GLYPH_CODES),
            "source_slot_count": len(PAIR_SOURCE_CODES),
            "glyph_code_pairs": {
                glyph: [f"0x{left:02X}", f"0x{right:02X}"]
                for glyph, (left, right) in PAIR_GLYPH_CODES.items()
            },
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

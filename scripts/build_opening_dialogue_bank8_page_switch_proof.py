#!/usr/bin/env python3
"""Build one bounded Bank 8 clone-page proof for the opening dialogue."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_16x16_proof import (
    add_target,
    build_square_glyph_tiles,
    changed_spans,
    default_square_font,
)
from build_opening_dialogue_8x16_proof import (
    BOTTOM_TILE_DELTA,
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
)
from build_opening_dialogue_proof import (
    BASE_MD5,
    ORIGINAL_RECORD,
    POINTER_INDEX,
    POINTER_ROM_OFFSET,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    resolve_base_rom,
)
from build_patch import make_records, write_ips
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


PAGE_CHR_BANK = 8
SOURCE_CHR_BANK = 7
CHR_BANK_SIZE = 0x2000
TILE_SIZE = 16
PHYSICAL_TILE_BASE = 0x100
HELPER_START_CODE = 0x81
HELPER_END_CODE_EXCLUSIVE = 0xCA
OUT_STEM = "kunio_period_drama_korean_opening_bank8_page_switch_proof"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_dialogue_bank8_page_switch_proof"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_page_switch_proof.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_page_switch_proof.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_page_switch_proof_font_preview.png"

# The short proof keeps the original record footprint. It validates a cloned
# CHR page and mapper state separately from pointer relocation.
PAGE_GLYPH_CODE_PAIRS: dict[str, tuple[int, int]] = {
    "쿠": (0x81, 0x82),
    "니": (0x83, 0x84),
    "마": (0x85, 0x86),
    "사": (0x87, 0x88),
    ":": (0xC8, 0xC9),
    "어": (0x89, 0x8A),
    "서": (0x8B, 0x8C),
}
RECORD_PREFIX = bytes.fromhex(
    "81 82 83 84 85 86 87 88 C8 C9 00 89 8A 8B 8C CA 00 FF"
)
PAGE_SWITCH_RECORD = RECORD_PREFIX + b"\x00" * (RECORD_LENGTH - len(RECORD_PREFIX))


def page_switch_helper() -> tuple[bytes, int]:
    """Return the target-record helper and its marker-hook CPU address."""

    entry = bytes.fromhex(
        "48 A5 1A C9 A6 D0 21 A5 1B C9 B1 D0 1B "
        "A9 40 8D 02 05 A9 42 8D 03 05 "
        "68 C9 81 90 0D C9 CA B0 09 85 1B 18 69 20 4C 6B 95 "
        "68 C9 00 D0 03 4C 6B 95 4C 63 95"
    )
    marker = bytes.fromhex(
        "A5 1B C9 81 90 0D C9 CA B0 09 48 A9 B1 85 1B 68 "
        "4C 8D 95 A9 00 4C 8D 95"
    )
    marker_cpu = CODE_CAVE_CPU + len(entry)
    helper = entry + marker
    if len(entry) != 51 or len(helper) != 75:
        raise AssertionError("page-switch helper layout changed unexpectedly")
    if len(helper) > CODE_CAVE_SIZE:
        raise AssertionError("page-switch helper does not fit the approved code cave")
    return helper, marker_cpu


def physical_tile_for_code(code: int) -> int:
    return PHYSICAL_TILE_BASE + code


def page_tile_offset(layout, code: int) -> int:
    physical_tile = physical_tile_for_code(code)
    if not 0 <= code <= 0xFF:
        raise ValueError(f"tile code out of range: 0x{code:X}")
    if not 0 <= PAGE_CHR_BANK < (layout.chr_end - layout.chr_start) // CHR_BANK_SIZE:
        raise ValueError(f"page CHR bank {PAGE_CHR_BANK} is outside this ROM")
    if not 0 <= physical_tile < CHR_BANK_SIZE // TILE_SIZE:
        raise ValueError(f"physical tile out of range: 0x{physical_tile:X}")
    return layout.chr_start + PAGE_CHR_BANK * CHR_BANK_SIZE + physical_tile * TILE_SIZE


def source_codes() -> tuple[int, ...]:
    return tuple(code for pair in PAGE_GLYPH_CODE_PAIRS.values() for code in pair)


def apply_page_switch_candidate(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
) -> tuple[bytes, list[dict[str, object]]]:
    if len(PAGE_SWITCH_RECORD) != RECORD_LENGTH or PAGE_SWITCH_RECORD[-20] != 0xFF:
        raise AssertionError("page-switch record layout changed unexpectedly")
    if base[RECORD_ROM_OFFSET : RECORD_ROM_OFFSET + RECORD_LENGTH] != ORIGINAL_RECORD:
        raise ValueError("opening source record does not match the verified base bytes")
    if (
        base[RENDER_ENTRY_ROM_OFFSET : RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)]
        != RENDER_ENTRY_ORIGINAL
    ):
        raise ValueError("renderer entry bytes do not match the verified base ROM")
    if (
        base[RENDER_MARKER_ROM_OFFSET : RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)]
        != RENDER_MARKER_ORIGINAL
    ):
        raise ValueError("renderer marker bytes do not match the verified base ROM")
    if base[CODE_CAVE_ROM_OFFSET : CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] != b"\xff" * CODE_CAVE_SIZE:
        raise ValueError("the approved renderer code cave is not untouched")

    helper, marker_cpu = page_switch_helper()
    layout = parse_ines_layout(base)
    patched = bytearray(base)
    targets: list[dict[str, object]] = []

    patched[RECORD_ROM_OFFSET : RECORD_ROM_OFFSET + RECORD_LENGTH] = PAGE_SWITCH_RECORD
    add_target(
        targets,
        kind="dialogue_record",
        rom_offset=RECORD_ROM_OFFSET,
        length=RECORD_LENGTH,
        pointer_rom_offset=POINTER_ROM_OFFSET,
    )

    source_start = layout.chr_start + SOURCE_CHR_BANK * CHR_BANK_SIZE
    page_start = layout.chr_start + PAGE_CHR_BANK * CHR_BANK_SIZE
    patched[page_start : page_start + CHR_BANK_SIZE] = base[
        source_start : source_start + CHR_BANK_SIZE
    ]
    add_target(
        targets,
        kind="chr_page_clone",
        rom_offset=page_start,
        length=CHR_BANK_SIZE,
        source_chr_bank=SOURCE_CHR_BANK,
        page_chr_bank=PAGE_CHR_BANK,
    )

    for glyph, (left_code, right_code) in PAGE_GLYPH_CODE_PAIRS.items():
        tiles = glyph_tiles.get(glyph)
        if tiles is None or len(tiles) != 4 or any(len(tile) != TILE_SIZE for tile in tiles):
            raise ValueError(f"missing four 8x8 tiles for {glyph!r}")
        placements = (
            ("font_tile_top_left", left_code, tiles[0]),
            ("font_tile_top_right", right_code, tiles[1]),
            ("font_tile_bottom_left", left_code + BOTTOM_TILE_DELTA, tiles[2]),
            ("font_tile_bottom_right", right_code + BOTTOM_TILE_DELTA, tiles[3]),
        )
        for kind, code, tile in placements:
            offset = page_tile_offset(layout, code)
            patched[offset : offset + TILE_SIZE] = tile
            add_target(
                targets,
                kind=kind,
                rom_offset=offset,
                length=TILE_SIZE,
                glyph=glyph,
                code=f"0x{code:02X}",
                physical_tile=f"0x{physical_tile_for_code(code):03X}",
                page_chr_bank=PAGE_CHR_BANK,
            )

    entry_hook = bytes((0x4C, CODE_CAVE_CPU & 0xFF, CODE_CAVE_CPU >> 8))
    marker_hook = bytes((0x4C, marker_cpu & 0xFF, marker_cpu >> 8))
    patched[RENDER_ENTRY_ROM_OFFSET : RENDER_ENTRY_ROM_OFFSET + len(entry_hook)] = entry_hook
    add_target(
        targets,
        kind="renderer_entry_hook",
        rom_offset=RENDER_ENTRY_ROM_OFFSET,
        length=len(entry_hook),
        cpu_address="0x955F",
    )
    patched[RENDER_MARKER_ROM_OFFSET : RENDER_MARKER_ROM_OFFSET + len(marker_hook)] = marker_hook
    add_target(
        targets,
        kind="renderer_marker_hook",
        rom_offset=RENDER_MARKER_ROM_OFFSET,
        length=len(marker_hook),
        cpu_address="0x9576",
        target_cpu_address=f"0x{marker_cpu:04X}",
    )
    patched[CODE_CAVE_ROM_OFFSET : CODE_CAVE_ROM_OFFSET + len(helper)] = helper
    add_target(
        targets,
        kind="renderer_helper_and_page_switch",
        rom_offset=CODE_CAVE_ROM_OFFSET,
        length=len(helper),
        cpu_address=f"0x{CODE_CAVE_CPU:04X}",
        page_r0="0x40",
        page_r1="0x42",
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
        raise AssertionError(f"candidate changed bytes outside its declared targets: {escaped[:8]}")
    return bytes(patched), targets


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    return "\n".join(
        [
            "# Opening Bank 8 Page-Switch Proof",
            "",
            f"Status: {payload['status']}",
            "",
            f"- Base MD5: {source['base_md5']}",
            f"- Pointer: {source['pointer_index']} at {source['record_rom_offset']}",
            f"- Display text: {source['korean_text']}",
            f"- Source CHR page: Bank {source['source_chr_bank']}",
            f"- Clone CHR page: Bank {source['page_chr_bank']}",
            f"- Mapper target: R0={source['page_r0']}, R1={source['page_r1']}",
            f"- Unique glyphs: {source['unique_glyph_count']}",
            f"- Candidate MD5: {candidate['patched_md5']}",
            f"- Declared changed spans: {candidate['changed_span_count']}",
            "",
            "This candidate proves only one opening-record page switch. Bank 8 ownership",
            "outside this bounded scene remains UNKNOWN until a page-conflict audit and",
            "additional scene captures are complete.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--font", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    args = parser.parse_args()

    base_path = resolve_base_rom(args.rom)
    base = base_path.read_bytes()
    actual_md5 = hashlib.md5(base).hexdigest()
    if actual_md5 != BASE_MD5:
        raise ValueError(f"unsupported base ROM MD5: {actual_md5}")
    font = default_square_font(args.font)
    glyph_tiles = build_square_glyph_tiles(font, PAGE_GLYPH_CODE_PAIRS)
    patched, targets = apply_page_switch_candidate(base, glyph_tiles)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    write_square_preview(
        list(PAGE_GLYPH_CODE_PAIRS),
        args.preview,
        font_path=font,
        target_pixels=15,
        threshold=100,
    )

    changed = changed_spans(base, patched)
    payload = {
        "status": "CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_PAGE_SWITCH",
        "source": {
            "base_md5": actual_md5,
            "pointer_index": POINTER_INDEX,
            "pointer_rom_offset": f"0x{POINTER_ROM_OFFSET:05X}",
            "record_rom_offset": f"0x{RECORD_ROM_OFFSET:05X}",
            "record_length": RECORD_LENGTH,
            "korean_text": "쿠니마사: 어서",
            "source_chr_bank": SOURCE_CHR_BANK,
            "page_chr_bank": PAGE_CHR_BANK,
            "page_r0": "0x40",
            "page_r1": "0x42",
            "helper_length": len(page_switch_helper()[0]),
            "unique_glyph_count": len(PAGE_GLYPH_CODE_PAIRS),
            "glyph_code_pairs": {
                glyph: [f"0x{left:02X}", f"0x{right:02X}"]
                for glyph, (left, right) in PAGE_GLYPH_CODE_PAIRS.items()
            },
        },
        "candidate": {
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": str(ips_path),
            "rom_path": str(rom_path),
            "ips_record_count": len(records),
            "changed_span_count": len(changed),
            "changed_spans": [
                {"start": f"0x{start:05X}", "end_exclusive": f"0x{end:05X}"}
                for start, end in changed
            ],
            "targets": targets,
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report_markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"ips={ips_path}")
    print(f"rom={rom_path}")
    print(f"report_json={args.report_json}")
    print(f"report_markdown={args.report_markdown}")
    print(f"base_md5={actual_md5}")
    print(f"patched_md5={payload['candidate']['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

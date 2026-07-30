#!/usr/bin/env python3
"""Build PTR-181 with a pointer-conditional fixed-bank CHR mapper wrapper."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_16x16_proof import (
    PAIR_GLYPH_CODES,
    add_target,
    build_square_glyph_tiles,
    changed_spans,
    default_square_font,
)
from build_opening_dialogue_8x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
)
from build_opening_dialogue_bank8_page_switch_proof import page_tile_offset
from build_opening_dialogue_bank8_page_switch_proof import page_switch_helper
from build_patch import make_records, write_ips
from build_ptr181_bank8_page_probe import (
    BASE_MD5,
    CHR_BANK_SIZE,
    POINTER_INDEX,
    POINTER_ROM_OFFSET,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    R1_WINDOW_BASE_CODE,
    R1_WINDOW_SIZE,
    TARGET_CPU,
    TEST_RECORD,
    resolve_base_rom,
)
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


MAPPER_WRAPPER_ROM_OFFSET = 0x1EE4F
MAPPER_WRAPPER_CPU = 0xEE3F
MAPPER_WRAPPER_ORIGINAL = bytes.fromhex(
    "AD 02 05 48 AD 03 05 48 A9 3C 8D 02 05 A9 3E 8D 03 05 "
    "20 D6 FE 68 8D 03 05 68 8D 02 05 60"
)
MAPPER_SELECT_CAVE_ROM_OFFSET = 0x1F2C1
MAPPER_SELECT_CAVE_CPU = 0xF2B1
MAPPER_SELECT_CAVE_SIZE = 28
MAPPER_STORE_CAVE_ROM_OFFSET = 0x1F2FE
MAPPER_STORE_CAVE_CPU = 0xF2EE
MAPPER_STORE_CAVE_SIZE = 26
OUT_STEM = "kunio_period_drama_korean_ptr181_conditional_mapper_probe"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "ptr181_conditional_mapper_probe"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "ptr181_conditional_mapper_probe.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "ptr181_conditional_mapper_probe.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "ptr181_conditional_mapper_probe_font_preview.png"


def mapper_helpers() -> tuple[bytes, bytes, bytes]:
    # Original wrapper saves $0502/$0503 before this JSR and restores them
    # after calling $FED6. This helper only chooses the temporary hardware page.
    store_normal_cpu = MAPPER_STORE_CAVE_CPU
    store_common_cpu = MAPPER_STORE_CAVE_CPU + 15
    select = bytes(
        (
            0xAD, 0xFF, 0x07, 0xC9, 0x01,
            0xD0, 0x10,
            0xA5, 0x51, 0xC9, 0x13,
            0xD0, 0x0A,
            0xA9, 0x3C, 0x8D, 0x02, 0x05, 0xA9, 0x46,
            0x4C, store_common_cpu & 0xFF, store_common_cpu >> 8,
            0x4C, store_normal_cpu & 0xFF, store_normal_cpu >> 8,
        )
    )
    store = bytes.fromhex(
        "A9 00 8D FF 07 A9 3C 8D 02 05 A9 3E EA EA EA 8D 03 05 60"
    )
    wrapper = bytearray(MAPPER_WRAPPER_ORIGINAL)
    wrapper[8:18] = bytes(
        (0x20, MAPPER_SELECT_CAVE_CPU & 0xFF, MAPPER_SELECT_CAVE_CPU >> 8)
    ) + b"\xEA" * 7
    if len(select) > MAPPER_SELECT_CAVE_SIZE or len(store) > MAPPER_STORE_CAVE_SIZE:
        raise AssertionError("conditional mapper helper exceeds fixed-bank cave")
    if len(wrapper) != len(MAPPER_WRAPPER_ORIGINAL):
        raise AssertionError("mapper wrapper footprint changed")
    return bytes(wrapper), select, store


def flagged_renderer_helper() -> tuple[bytes, int]:
    helper, marker_cpu = page_switch_helper()
    helper = bytearray(helper)
    expected = bytes.fromhex("A9 40 8D 02 05 A9 42 8D 03 05")
    offset = bytes(helper).find(expected)
    if offset < 0:
        raise AssertionError("page helper mapper-write block not found")
    helper[offset:offset + len(expected)] = bytes.fromhex(
        "A9 01 8D FF 07 EA EA EA EA EA"
    )
    helper[4] = TARGET_CPU & 0xFF
    if helper[10] != TARGET_CPU >> 8:
        raise AssertionError("page helper target high byte changed")
    return bytes(helper), marker_cpu


def patch_candidate(base: bytes, font_path: Path) -> tuple[bytes, list[dict[str, object]]]:
    if hashlib.md5(base).hexdigest() != BASE_MD5:
        raise ValueError("unsupported base ROM")
    if base[MAPPER_WRAPPER_ROM_OFFSET:MAPPER_WRAPPER_ROM_OFFSET + 30] != MAPPER_WRAPPER_ORIGINAL:
        raise ValueError("fixed mapper wrapper does not match base ROM")
    if base[MAPPER_SELECT_CAVE_ROM_OFFSET:MAPPER_SELECT_CAVE_ROM_OFFSET + MAPPER_SELECT_CAVE_SIZE] != b"\0" * MAPPER_SELECT_CAVE_SIZE:
        raise ValueError("mapper select cave is not untouched zero fill")
    if base[MAPPER_STORE_CAVE_ROM_OFFSET:MAPPER_STORE_CAVE_ROM_OFFSET + MAPPER_STORE_CAVE_SIZE] != b"\0" * MAPPER_STORE_CAVE_SIZE:
        raise ValueError("mapper store cave is not untouched zero fill")
    if base[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + 3] != RENDER_ENTRY_ORIGINAL:
        raise ValueError("renderer entry bytes changed")
    if base[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + 3] != RENDER_MARKER_ORIGINAL:
        raise ValueError("renderer marker bytes changed")
    if base[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] != b"\xFF" * CODE_CAVE_SIZE:
        raise ValueError("renderer cave is not untouched")

    layout = parse_ines_layout(base)
    patched = bytearray(base)
    targets: list[dict[str, object]] = []
    glyph_tiles = build_square_glyph_tiles(font_path, PAIR_GLYPH_CODES)
    renderer, marker_cpu = flagged_renderer_helper()
    wrapper, select, store = mapper_helpers()

    patched[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + 3] = bytes(
        (0x4C, CODE_CAVE_CPU & 0xFF, CODE_CAVE_CPU >> 8)
    )
    patched[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + 3] = bytes(
        (0x4C, marker_cpu & 0xFF, marker_cpu >> 8)
    )
    patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + len(renderer)] = renderer
    add_target(targets, kind="renderer_entry_hook", rom_offset=RENDER_ENTRY_ROM_OFFSET, length=3)
    add_target(targets, kind="renderer_marker_hook", rom_offset=RENDER_MARKER_ROM_OFFSET, length=3)
    add_target(targets, kind="paired_renderer_helper", rom_offset=CODE_CAVE_ROM_OFFSET, length=len(renderer))

    page_start = page_tile_offset(layout, R1_WINDOW_BASE_CODE)
    source_start = page_start - CHR_BANK_SIZE
    patched[page_start:page_start + R1_WINDOW_SIZE] = base[source_start:source_start + R1_WINDOW_SIZE]
    add_target(targets, kind="chr_page_clone", rom_offset=page_start, length=R1_WINDOW_SIZE)
    for glyph, pair in PAIR_GLYPH_CODES.items():
        for index, code in enumerate((pair[0], pair[1], pair[0] + 0x20, pair[1] + 0x20)):
            offset = page_tile_offset(layout, code)
            patched[offset:offset + 16] = glyph_tiles[glyph][index]
            add_target(targets, kind="font_tile_page", rom_offset=offset, length=16, glyph=glyph)

    patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = TEST_RECORD
    add_target(targets, kind="ptr181_dialogue_record", rom_offset=RECORD_ROM_OFFSET, length=RECORD_LENGTH)
    for kind, offset, data in (
        ("conditional_mapper_wrapper", MAPPER_WRAPPER_ROM_OFFSET, wrapper),
        ("conditional_mapper_select", MAPPER_SELECT_CAVE_ROM_OFFSET, select),
        ("conditional_mapper_store", MAPPER_STORE_CAVE_ROM_OFFSET, store),
    ):
        patched[offset:offset + len(data)] = data
        add_target(targets, kind=kind, rom_offset=offset, length=len(data))

    allowed = [(int(t["rom_offset"]), int(t["rom_offset"]) + int(t["length"])) for t in targets]
    escaped = [
        offset for offset, (old, new) in enumerate(zip(base, patched))
        if old != new and not any(start <= offset < end for start, end in allowed)
    ]
    if escaped:
        raise AssertionError(f"candidate escaped allowlist: {escaped[:8]}")
    return bytes(patched), targets


def render_report(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "# PTR-181 Conditional Mapper Probe",
            "",
            f"Status: **{payload['status']}**",
            "",
            f"- Base MD5: `{payload['base_md5']}`",
            f"- Candidate MD5: `{payload['candidate_md5']}`",
            "- Mapper policy: the PTR-181 scene flag with `$51=13` selects `R0/R1=3C/46`; all other contexts select original `3C/3E`.",
            "- The original fixed-bank wrapper still saves and restores `$0502/$0503`.",
            "",
            "This is a bounded renderer/page-lifecycle candidate, not release prose.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?")
    parser.add_argument("--font", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    base_path = resolve_base_rom(args.rom)
    base = base_path.read_bytes()
    patched, targets = patch_candidate(base, default_square_font(args.font))
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    write_square_preview(list(PAIR_GLYPH_CODES), DEFAULT_PREVIEW, font_path=default_square_font(args.font), target_pixels=15, threshold=100)
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_RUNTIME_PROOF",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(patched).hexdigest(),
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
        "changed_span_count": len(changed_spans(base, patched)),
        "targets": targets,
    }
    DEFAULT_REPORT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    DEFAULT_REPORT_MARKDOWN.write_text(render_report(payload), encoding="utf-8")
    print(f"rom={rom_path}")
    print(f"candidate_md5={payload['candidate_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

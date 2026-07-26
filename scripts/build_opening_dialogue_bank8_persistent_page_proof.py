#!/usr/bin/env python3
"""Build a bounded Bank 8 page proof with a persistent MMC3 R0/R1 override."""

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
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
)
from build_opening_dialogue_bank8_page_switch_proof import (
    CHR_BANK_SIZE,
    PAGE_CHR_BANK,
    PAGE_GLYPH_CODE_PAIRS,
    PAGE_SWITCH_RECORD,
    SOURCE_CHR_BANK,
    TILE_SIZE,
    page_tile_offset,
    physical_tile_for_code,
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


FLAG_RAM = 0x04FE
MAPPER_R0_LOAD_CPU = 0xFEDD
MAPPER_R0_LOAD_ROM_OFFSET = 0x1FEED
MAPPER_R0_LOAD_ORIGINAL = bytes.fromhex("AD 02 05")
MAPPER_R0_CONTINUATION_CPU = 0xFEE0
OUT_STEM = "kunio_period_drama_korean_opening_bank8_persistent_page_proof"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_dialogue_bank8_persistent_page_proof"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_persistent_page_proof.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_persistent_page_proof.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_persistent_page_proof_font_preview.png"


def persistent_page_switch_helper() -> tuple[bytes, int, int]:
    """Return renderer, marker, and fixed-mapper helper entry points.

    The renderer sets a proof-local flag after pointer 182 begins. The fixed
    MMC3 R0 loader then supplies Bank 8's R0/R1 pair on every update. This is
    intentionally a bounded persistence proof, not release page lifecycle code.
    """

    entry = bytes.fromhex(
        "48 A5 1A C9 A6 D0 1C A5 1B C9 B1 D0 16 "
        "A9 01 8D FE 04 "
        "68 C9 81 90 0D C9 CA B0 09 85 1B 18 69 20 4C 6B 95 "
        "68 C9 00 D0 03 4C 6B 95 4C 63 95"
    )
    marker = bytes.fromhex(
        "A5 1B C9 81 90 0D C9 CA B0 09 48 A9 B1 85 1B 68 "
        "4C 8D 95 A9 00 4C 8D 95"
    )
    mapper = bytes.fromhex(
        "AD FE 04 F0 0A A9 42 8D 03 05 A9 40 4C E0 FE "
        "AD 02 05 4C E0 FE"
    )
    marker_cpu = CODE_CAVE_CPU + len(entry)
    mapper_cpu = marker_cpu + len(marker)
    helper = entry + marker + mapper
    if len(entry) != 46 or len(marker) != 24 or len(mapper) != 21:
        raise AssertionError("persistent page helper layout changed unexpectedly")
    if len(helper) != CODE_CAVE_SIZE:
        raise AssertionError("persistent page helper must exactly occupy its approved cave")
    return helper, marker_cpu, mapper_cpu


def apply_persistent_page_candidate(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
) -> tuple[bytes, list[dict[str, object]]]:
    if len(PAGE_SWITCH_RECORD) != RECORD_LENGTH or PAGE_SWITCH_RECORD[-20] != 0xFF:
        raise AssertionError("persistent proof record layout changed unexpectedly")
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
    if (
        base[MAPPER_R0_LOAD_ROM_OFFSET : MAPPER_R0_LOAD_ROM_OFFSET + len(MAPPER_R0_LOAD_ORIGINAL)]
        != MAPPER_R0_LOAD_ORIGINAL
    ):
        raise ValueError("fixed MMC3 R0 load bytes do not match the verified base ROM")
    if base[CODE_CAVE_ROM_OFFSET : CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] != b"\xff" * CODE_CAVE_SIZE:
        raise ValueError("the approved renderer code cave is not untouched")

    helper, marker_cpu, mapper_cpu = persistent_page_switch_helper()
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
            ("font_tile_bottom_left", left_code + 0x20, tiles[2]),
            ("font_tile_bottom_right", right_code + 0x20, tiles[3]),
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
    mapper_hook = bytes((0x4C, mapper_cpu & 0xFF, mapper_cpu >> 8))
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
    patched[MAPPER_R0_LOAD_ROM_OFFSET : MAPPER_R0_LOAD_ROM_OFFSET + len(mapper_hook)] = mapper_hook
    add_target(
        targets,
        kind="fixed_mapper_r0_load_hook",
        rom_offset=MAPPER_R0_LOAD_ROM_OFFSET,
        length=len(mapper_hook),
        cpu_address=f"0x{MAPPER_R0_LOAD_CPU:04X}",
        target_cpu_address=f"0x{mapper_cpu:04X}",
    )
    patched[CODE_CAVE_ROM_OFFSET : CODE_CAVE_ROM_OFFSET + len(helper)] = helper
    add_target(
        targets,
        kind="renderer_marker_and_persistent_mapper_helper",
        rom_offset=CODE_CAVE_ROM_OFFSET,
        length=len(helper),
        cpu_address=f"0x{CODE_CAVE_CPU:04X}",
        flag_ram=f"0x{FLAG_RAM:04X}",
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
            "# Opening Bank 8 Persistent Page Proof",
            "",
            f"Status: {payload['status']}",
            "",
            f"- Base MD5: {source['base_md5']}",
            f"- Pointer: {source['pointer_index']} at {source['record_rom_offset']}",
            f"- Display text: {source['korean_text']}",
            f"- Source/clone CHR pages: Bank {source['source_chr_bank']} -> Bank {source['page_chr_bank']}",
            f"- Persistent mapper pair: R0={source['page_r0']}, R1={source['page_r1']}",
            f"- Activation flag: {source['flag_ram']}",
            f"- Unique glyphs: {source['unique_glyph_count']}",
            f"- Candidate MD5: {candidate['patched_md5']}",
            "",
            "The flag deliberately has no release lifecycle yet. A PASS only proves",
            "that the fixed opening route keeps the cloned page visible; it does not",
            "authorize Bank 8 or the flag address in other scenes.",
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
    glyph_tiles = build_square_glyph_tiles(default_square_font(args.font), PAGE_GLYPH_CODE_PAIRS)
    patched, targets = apply_persistent_page_candidate(base, glyph_tiles)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    write_square_preview(
        list(PAGE_GLYPH_CODE_PAIRS),
        args.preview,
        font_path=default_square_font(args.font),
        target_pixels=15,
        threshold=100,
    )

    changed = changed_spans(base, patched)
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_BOUNDED_PERSISTENCE_PROOF",
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
            "flag_ram": f"0x{FLAG_RAM:04X}",
            "helper_length": len(persistent_page_switch_helper()[0]),
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

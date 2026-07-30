#!/usr/bin/env python3
"""Build a PTR-181 probe with renderer-entry-only CHR page switching."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_8x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
)
from build_opening_dialogue_16x16_proof import (
    PAIR_GLYPH_CODES,
    add_target,
    build_square_glyph_tiles,
    default_square_font,
    changed_spans,
)
from build_opening_dialogue_bank8_page_switch_proof import page_switch_helper, page_tile_offset
from build_patch import make_records, write_ips
from build_ptr181_bank8_page_probe import (
    BASE_MD5,
    CHR_BANK_SIZE,
    POINTER_INDEX,
    POINTER_ROM_OFFSET,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    TARGET_CPU,
    TEST_RECORD,
    resolve_base_rom,
)
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


R1_WINDOW_BASE_CODE = 0x80
R1_WINDOW_SIZE = 0x800
SOURCE_LOW_COMPARE = bytes.fromhex("C9 A6 D0")
OUT_STEM = "kunio_period_drama_korean_ptr181_dynamic_page_probe"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "ptr181_dynamic_page_probe"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "ptr181_dynamic_page_probe.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "ptr181_dynamic_page_probe.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "ptr181_dynamic_page_probe_font_preview.png"


def retarget_helper() -> tuple[bytes, int]:
    helper, marker_cpu = page_switch_helper()
    helper = bytearray(helper)
    if bytes(helper[3:6]) != SOURCE_LOW_COMPARE:
        raise AssertionError("dynamic page helper target layout changed")
    helper[4] = TARGET_CPU & 0xFF
    if bytes(helper[3:6]) != bytes((0xC9, TARGET_CPU & 0xFF, 0xD0)):
        raise AssertionError("dynamic PTR-181 helper retarget failed")
    return bytes(helper), marker_cpu


def patch_candidate(base: bytes, font_path: Path) -> tuple[bytes, list[dict[str, object]]]:
    if hashlib.md5(base).hexdigest() != BASE_MD5:
        raise ValueError("unsupported base ROM")
    if int.from_bytes(base[POINTER_ROM_OFFSET:POINTER_ROM_OFFSET + 2], "little") != TARGET_CPU:
        raise ValueError("PTR-181 pointer entry does not map to CPU $B188")
    if len(TEST_RECORD) != RECORD_LENGTH:
        raise AssertionError("PTR-181 test record footprint changed")
    if base[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] != RENDER_ENTRY_ORIGINAL:
        raise ValueError("renderer entry bytes do not match the verified base ROM")
    if base[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] != RENDER_MARKER_ORIGINAL:
        raise ValueError("renderer marker bytes do not match the verified base ROM")
    if base[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] != b"\xff" * CODE_CAVE_SIZE:
        raise ValueError("renderer code cave is not untouched")

    helper, marker_cpu = retarget_helper()
    glyph_tiles = build_square_glyph_tiles(font_path, PAIR_GLYPH_CODES)
    layout = parse_ines_layout(base)
    expanded = bytearray(base)
    targets: list[dict[str, object]] = []

    entry_hook = bytes((0x4C, CODE_CAVE_CPU & 0xFF, CODE_CAVE_CPU >> 8))
    marker_hook = bytes((0x4C, marker_cpu & 0xFF, marker_cpu >> 8))
    expanded[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + 3] = entry_hook
    expanded[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + 3] = marker_hook
    expanded[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + len(helper)] = helper
    add_target(targets, kind="renderer_entry_hook", rom_offset=RENDER_ENTRY_ROM_OFFSET, length=3, cpu_address="0x955F")
    add_target(targets, kind="renderer_marker_hook", rom_offset=RENDER_MARKER_ROM_OFFSET, length=3, cpu_address="0x9576")
    add_target(targets, kind="renderer_helper", rom_offset=CODE_CAVE_ROM_OFFSET, length=len(helper), cpu_address=f"0x{CODE_CAVE_CPU:04X}", page_r0="0x40", page_r1="0x42")

    page_start = page_tile_offset(layout, R1_WINDOW_BASE_CODE)
    source_start = page_start - CHR_BANK_SIZE
    expanded[page_start:page_start + R1_WINDOW_SIZE] = base[source_start:source_start + R1_WINDOW_SIZE]
    add_target(targets, kind="chr_page_clone_from_bank7", rom_offset=page_start, length=R1_WINDOW_SIZE, source_chr_bank=7, target_chr_bank=8)
    for glyph, pair in PAIR_GLYPH_CODES.items():
        tiles = glyph_tiles[glyph]
        for index, code in enumerate((pair[0], pair[1], pair[0] + 0x20, pair[1] + 0x20)):
            offset = page_tile_offset(layout, code)
            expanded[offset:offset + 16] = tiles[index]
            add_target(targets, kind="font_tile_page", rom_offset=offset, length=16, glyph=glyph, code=f"0x{code:02X}", chr_bank=8)

    expanded[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = TEST_RECORD
    add_target(targets, kind="ptr181_dialogue_record", rom_offset=RECORD_ROM_OFFSET, length=RECORD_LENGTH, pointer_index=POINTER_INDEX, pointer_rom_offset=POINTER_ROM_OFFSET, cpu_address=f"0x{TARGET_CPU:04X}")

    allowed = [(int(target["rom_offset"]), int(target["rom_offset"]) + int(target["length"])) for target in targets]
    escaped = [offset for offset, (old, new) in enumerate(zip(base, expanded)) if old != new and not any(start <= offset < end for start, end in allowed)]
    if escaped:
        raise AssertionError(f"dynamic PTR-181 candidate changed bytes outside its allowlist: {escaped[:8]}")
    return bytes(expanded), targets


def render_report(payload: dict[str, object]) -> str:
    candidate = payload["candidate"]
    return "\n".join([
        "# PTR-181 Dynamic Bank 8 Page Probe",
        "",
        f"Status: {payload['status']}",
        "",
        f"- Base MD5: `{payload['base_md5']}`",
        f"- Pointer: `{POINTER_INDEX}` / CPU `${TARGET_CPU:04X}` / ROM `0x{RECORD_ROM_OFFSET:05X}`",
        "- Page switch: renderer entry only, R0/R1 `40/42`; normal mapper setup is untouched",
        f"- Candidate MD5: `{candidate['patched_md5']}`",
        f"- Declared changed spans: `{candidate['changed_span_count']}`",
        "",
        "This is a renderer/font ownership probe. The text is deliberately a",
        "glyph-coverage test and is not release translation prose.",
        "",
    ])


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
    patched, targets = patch_candidate(base, default_square_font(args.font))
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    write_square_preview(list(PAIR_GLYPH_CODES), args.preview, font_path=default_square_font(args.font), target_pixels=15, threshold=100)
    candidate = {"patched_md5": hashlib.md5(patched).hexdigest(), "ips_path": str(ips_path.relative_to(REPO_ROOT)), "rom_path": str(rom_path.relative_to(REPO_ROOT)), "ips_record_count": len(records), "changed_span_count": len(changed_spans(base, patched)), "target_count": len(targets), "targets": targets}
    payload = {"status": "CANDIDATE_BUILT_PENDING_PTR181_DYNAMIC_RUNTIME_PROOF", "base_md5": hashlib.md5(base).hexdigest(), "pointer_index": POINTER_INDEX, "pointer_rom_offset": f"0x{POINTER_ROM_OFFSET:05X}", "record_rom_offset": f"0x{RECORD_ROM_OFFSET:05X}", "record_length": RECORD_LENGTH, "test_record": TEST_RECORD.hex(" ").upper(), "candidate": candidate}
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"ips={ips_path}")
    print(f"rom={rom_path}")
    print(f"patched_md5={candidate['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

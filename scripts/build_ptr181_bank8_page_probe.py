#!/usr/bin/env python3
"""Build a renderer-scoped Bank 8 probe for the visible PTR-181 record.

This candidate keeps the original Bank 7 window intact, clones the relevant
window into Bank 8, and retargets the proven paired-cell helper from PTR-182
to PTR-181. The inserted text is a glyph-coverage probe, not release prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_16x16_proof import (
    PAIR_GLYPH_CODES,
    add_target,
    apply_paired_renderer_assets,
    build_square_glyph_tiles,
    default_square_font,
    changed_spans,
)
from build_opening_dialogue_8x16_proof import HELPER_CODE
from build_opening_dialogue_bank8_page_switch_proof import page_tile_offset
from build_patch import make_records, write_ips
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


BASE_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
POINTER_INDEX = 181
POINTER_ROM_OFFSET = 0x05F3E
TARGET_CPU = 0xB188
RECORD_ROM_OFFSET = 0x07198
RECORD_LENGTH = 0x071B6 - RECORD_ROM_OFFSET
CHR_BANK_SIZE = 0x2000
R1_WINDOW_BASE_CODE = 0x80
R1_WINDOW_SIZE = 0x800
MAPPER_SETUP_ROM_OFFSET = 0x1EE57
MAPPER_SETUP_ORIGINAL = bytes.fromhex("A9 3C 8D 02 05 A9 3E 8D 03 05")
STATIC_R1 = 0x46
TARGET_LOW_COMPARE = bytes.fromhex("C9 A6 D0")
TEST_RECORD = bytes.fromhex(
    "81 8C 82 8D 83 8E 84 8F 85 90 86 91 87 92 88 93 "
    "CA 00 FF"
) + b"\x00" * 11
OUT_STEM = "kunio_period_drama_korean_ptr181_bank8_page_probe"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "ptr181_bank8_page_probe"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "ptr181_bank8_page_probe.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "ptr181_bank8_page_probe.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "ptr181_bank8_page_probe_font_preview.png"


def resolve_base_rom(candidate: str | Path | None) -> Path:
    if candidate is not None:
        return Path(candidate).expanduser().resolve()
    matches = sorted((REPO_ROOT / "rom").glob("*.nes"))
    if not matches:
        raise FileNotFoundError("No base ROM found under rom/")
    return matches[0]


def retarget_helper() -> bytes:
    helper = bytearray(HELPER_CODE)
    if bytes(helper[3:6]) != TARGET_LOW_COMPARE:
        raise AssertionError("the paired renderer helper target layout changed")
    helper[4] = TARGET_CPU & 0xFF
    if bytes(helper[3:6]) != bytes((0xC9, TARGET_CPU & 0xFF, 0xD0)):
        raise AssertionError("PTR-181 helper retarget failed")
    return bytes(helper)


def patch_page_assets(
    base: bytes,
    font_path: Path,
) -> tuple[bytes, list[dict[str, object]]]:
    if hashlib.md5(base).hexdigest() != BASE_MD5:
        raise ValueError("unsupported base ROM")
    if len(TEST_RECORD) != RECORD_LENGTH or TEST_RECORD[-1] != 0:
        raise AssertionError("PTR-181 test record footprint changed")
    if int.from_bytes(base[POINTER_ROM_OFFSET:POINTER_ROM_OFFSET + 2], "little") != TARGET_CPU:
        raise ValueError("PTR-181 pointer entry does not map to CPU $B188")

    glyph_tiles = build_square_glyph_tiles(font_path, PAIR_GLYPH_CODES)
    helper = retarget_helper()
    patched, raw_targets = apply_paired_renderer_assets(
        base,
        glyph_tiles,
        glyph_code_pairs=PAIR_GLYPH_CODES,
        helper_code=helper,
        helper_start_code=0x81,
        helper_end_code_exclusive=0x94,
    )
    expanded = bytearray(patched)
    targets: list[dict[str, object]] = []
    for target in raw_targets:
        kind = str(target.get("kind", ""))
        if kind.startswith("font_tile_"):
            offset = int(target["rom_offset"])
            length = int(target["length"])
            expanded[offset:offset + length] = base[offset:offset + length]
            continue
        targets.append(target)

    layout = parse_ines_layout(base)
    page_start = page_tile_offset(layout, R1_WINDOW_BASE_CODE)
    source_start = page_start - CHR_BANK_SIZE
    expanded[page_start:page_start + R1_WINDOW_SIZE] = base[source_start:source_start + R1_WINDOW_SIZE]
    add_target(
        targets,
        kind="chr_page_clone_from_bank7",
        rom_offset=page_start,
        length=R1_WINDOW_SIZE,
        source_window=f"0x{source_start:05X}",
        target_window=f"0x{page_start:05X}",
        source_chr_bank=7,
        target_chr_bank=8,
    )

    for glyph, pair in PAIR_GLYPH_CODES.items():
        tiles = glyph_tiles[glyph]
        for index, code in enumerate((pair[0], pair[1], pair[0] + 0x20, pair[1] + 0x20)):
            offset = page_tile_offset(layout, code)
            expanded[offset:offset + 16] = tiles[index]
            add_target(
                targets,
                kind="font_tile_page",
                rom_offset=offset,
                length=16,
                glyph=glyph,
                code=f"0x{code:02X}",
                chr_bank=8,
            )

    if base[MAPPER_SETUP_ROM_OFFSET:MAPPER_SETUP_ROM_OFFSET + len(MAPPER_SETUP_ORIGINAL)] != MAPPER_SETUP_ORIGINAL:
        raise ValueError("normal mapper setup does not match the verified base ROM")
    expanded[MAPPER_SETUP_ROM_OFFSET + 6] = STATIC_R1
    add_target(
        targets,
        kind="static_normal_mapper_r1",
        rom_offset=MAPPER_SETUP_ROM_OFFSET + 6,
        length=1,
        original="0x3E",
        replacement=f"0x{STATIC_R1:02X}",
    )

    expanded[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = TEST_RECORD
    add_target(
        targets,
        kind="ptr181_dialogue_record",
        rom_offset=RECORD_ROM_OFFSET,
        length=RECORD_LENGTH,
        pointer_index=POINTER_INDEX,
        pointer_rom_offset=POINTER_ROM_OFFSET,
        cpu_address=f"0x{TARGET_CPU:04X}",
    )

    allowed = [
        (int(target["rom_offset"]), int(target["rom_offset"]) + int(target["length"]))
        for target in targets
    ]
    escaped = [
        offset
        for offset, (old, new) in enumerate(zip(base, expanded))
        if old != new and not any(start <= offset < end for start, end in allowed)
    ]
    if escaped:
        raise AssertionError(f"PTR-181 candidate changed bytes outside its allowlist: {escaped[:8]}")
    if expanded[0x1C000:0x1C800] != base[0x1C000:0x1C800]:
        raise AssertionError("Bank 7 font source window was changed")
    return bytes(expanded), targets


def render_report(payload: dict[str, object]) -> str:
    candidate = payload["candidate"]
    return "\n".join([
        "# PTR-181 Bank 8 Page Probe",
        "",
        f"Status: {payload['status']}",
        "",
        f"- Base MD5: `{payload['base_md5']}`",
        f"- Pointer: `{POINTER_INDEX}` / CPU `${TARGET_CPU:04X}` / ROM `0x{RECORD_ROM_OFFSET:05X}`",
        f"- Test record length: `{RECORD_LENGTH}` bytes",
        f"- Cloned window: Bank 7 -> Bank 8, R1 `3E -> {STATIC_R1:02X}`",
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
    font_path = default_square_font(args.font)
    patched, targets = patch_page_assets(base, font_path)
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    write_square_preview(list(PAIR_GLYPH_CODES), args.preview, font_path=font_path, target_pixels=15, threshold=100)

    candidate = {
        "patched_md5": hashlib.md5(patched).hexdigest(),
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
        "ips_record_count": len(records),
        "changed_span_count": len(changed_spans(base, patched)),
        "target_count": len(targets),
        "targets": targets,
    }
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_PTR181_RUNTIME_PROOF",
        "base_md5": hashlib.md5(base).hexdigest(),
        "pointer_index": POINTER_INDEX,
        "pointer_rom_offset": f"0x{POINTER_ROM_OFFSET:05X}",
        "record_rom_offset": f"0x{RECORD_ROM_OFFSET:05X}",
        "record_length": RECORD_LENGTH,
        "test_record": TEST_RECORD.hex(" ").upper(),
        "candidate": candidate,
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"ips={ips_path}")
    print(f"rom={rom_path}")
    print(f"patched_md5={candidate['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

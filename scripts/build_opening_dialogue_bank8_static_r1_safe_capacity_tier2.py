#!/usr/bin/env python3
"""Build a tier-2 opening candidate with isolated Bank 8 font assets.

The first static-R1 tier-2 candidate patched the source Bank 7 font slots and
then cloned that damaged page. This builder keeps Bank 7 byte-for-byte intact,
clones the original page, and writes the expanded Korean glyphs only into the
runtime Bank 8 page.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_16x16_capacity import (
    DEFAULT_CATALOG,
    apply_capacity_candidate,
    validate_capacity_catalog,
)
from build_opening_dialogue_16x16_proof import (
    add_target,
    build_square_glyph_tiles,
    default_square_font,
)
from build_opening_dialogue_8x16_proof import BOTTOM_TILE_DELTA
from build_opening_dialogue_bank8_page_switch_proof import (
    PAGE_CHR_BANK,
    page_tile_offset,
    physical_tile_for_code,
)
from build_opening_dialogue_proof import BASE_MD5, resolve_base_rom
from build_patch import make_records, write_ips
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


SOURCE_CHR_BANK = 7
TARGET_CHR_BANK = PAGE_CHR_BANK
R1_WINDOW_BASE_CODE = 0x80
R1_WINDOW_SIZE = 0x800
TILE_SIZE = 16
MAPPER_SETUP_ROM_OFFSET = 0x1EE57
MAPPER_SETUP_ORIGINAL = bytes.fromhex("A9 3C 8D 02 05 A9 3E 8D 03 05")
STATIC_R1 = 0x46
OUT_STEM = "kunio_period_drama_korean_opening_bank8_static_r1_safe_capacity_tier2"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_dialogue_bank8_static_r1_safe_capacity_tier2"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_safe_capacity_tier2.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_safe_capacity_tier2.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_safe_capacity_tier2_font_preview.png"


def apply_candidate(
    base: bytes,
    config: dict[str, object],
    font_path: Path,
) -> tuple[bytes, list[dict[str, object]]]:
    profile = config["profile"]
    assert isinstance(profile, dict)
    pairs = profile["glyph_code_pairs"]
    assert isinstance(pairs, dict)
    glyph_tiles = build_square_glyph_tiles(font_path, pairs)

    # Reuse the proven record/helper relocation, then remove only the source
    # Bank 7 font writes before constructing the isolated page.
    patched, raw_targets = apply_capacity_candidate(base, glyph_tiles, config)
    expanded = bytearray(patched)
    targets: list[dict[str, object]] = []
    for target in raw_targets:
        kind = str(target.get("kind", ""))
        if kind.startswith("font_tile_"):
            offset = int(target["rom_offset"])
            length = int(target["length"])
            if expanded[offset : offset + length] == base[offset : offset + length]:
                raise AssertionError("capacity helper did not write the expected source font tile")
            expanded[offset : offset + length] = base[offset : offset + length]
            continue
        targets.append(target)

    layout = parse_ines_layout(base)
    target_start = page_tile_offset(layout, R1_WINDOW_BASE_CODE)
    source_start = target_start - 0x2000
    expanded[target_start : target_start + R1_WINDOW_SIZE] = base[source_start : source_start + R1_WINDOW_SIZE]
    targets.append(
        {
            "kind": "chr_page_clone_from_base_source",
            "rom_offset": target_start,
            "length": R1_WINDOW_SIZE,
            "source_chr_bank": SOURCE_CHR_BANK,
            "target_chr_bank": TARGET_CHR_BANK,
            "source_window": f"0x{source_start:05X}",
            "target_window": f"0x{target_start:05X}",
        }
    )

    for glyph, (left_code, right_code) in pairs.items():
        tiles = glyph_tiles[glyph]
        placements = (
            ("font_tile_page_top_left", left_code, tiles[0]),
            ("font_tile_page_top_right", right_code, tiles[1]),
            ("font_tile_page_bottom_left", left_code + BOTTOM_TILE_DELTA, tiles[2]),
            ("font_tile_page_bottom_right", right_code + BOTTOM_TILE_DELTA, tiles[3]),
        )
        for kind, code, tile in placements:
            offset = page_tile_offset(layout, code)
            expanded[offset : offset + TILE_SIZE] = tile
            add_target(
                targets,
                kind=kind,
                rom_offset=offset,
                length=TILE_SIZE,
                glyph=glyph,
                code=f"0x{code:02X}",
                physical_tile=f"0x{physical_tile_for_code(code):03X}",
                page_chr_bank=TARGET_CHR_BANK,
            )

    r1_immediate = MAPPER_SETUP_ROM_OFFSET + 6
    if base[MAPPER_SETUP_ROM_OFFSET : MAPPER_SETUP_ROM_OFFSET + len(MAPPER_SETUP_ORIGINAL)] != MAPPER_SETUP_ORIGINAL:
        raise ValueError("normal mapper setup does not match the verified base ROM")
    expanded[r1_immediate] = STATIC_R1
    targets.append(
        {
            "kind": "static_normal_mapper_r1",
            "rom_offset": r1_immediate,
            "length": 1,
            "cpu_address": "0xEE4D",
            "original": "0x3E",
            "replacement": f"0x{STATIC_R1:02X}",
        }
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
        raise AssertionError(f"candidate changed bytes outside declared targets: {escaped[:8]}")
    source_start = target_start - 0x2000
    if expanded[source_start : source_start + R1_WINDOW_SIZE] != base[source_start : source_start + R1_WINDOW_SIZE]:
        raise AssertionError("isolated page candidate changed source Bank 7")
    return bytes(expanded), targets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG.parent / "opening_ptr_182_16x16_capacity_tier2.json")
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
    config = validate_capacity_catalog(args.catalog)
    font_path = default_square_font(args.font)
    patched, targets = apply_candidate(base, config, font_path)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    pairs = config["profile"]["glyph_code_pairs"]
    write_square_preview(list(pairs), args.preview, font_path=font_path, target_pixels=15, threshold=100)

    record = config["record"]
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_SAFE_STATIC_R1_CAPACITY_PROOF",
        "source": {
            "base_md5": actual_md5,
            "catalog": str(args.catalog.relative_to(REPO_ROOT)),
            "catalog_sha256": config["catalog_sha256"],
            "pointer_index": record["pointer_index"],
            "record_rom_offset": record["record_rom_offset"],
            "record_length": len(config["encoded"]),
            "source_chr_bank": SOURCE_CHR_BANK,
            "target_chr_bank": TARGET_CHR_BANK,
            "static_r1": f"0x{STATIC_R1:02X}",
            "glyph_count": len(pairs),
            "glyph_code_pairs": {
                glyph: [f"0x{left:02X}", f"0x{right:02X}"]
                for glyph, (left, right) in pairs.items()
            },
        },
        "candidate": {
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": str(ips_path.relative_to(REPO_ROOT)),
            "rom_path": str(rom_path.relative_to(REPO_ROOT)),
            "ips_record_count": len(records),
            "target_count": len(targets),
            "targets": targets,
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(
        "\n".join(
            [
                "# Opening Bank 8 Static R1 Safe Capacity Tier-2 Proof",
                "",
                f"Status: {payload['status']}",
                "",
                f"- Base MD5: `{actual_md5}`",
                f"- Pointer `{record['pointer_index']}` record: `{record['record_rom_offset']}`, `{len(config['encoded'])}` bytes",
                f"- Korean glyphs/source pairs: `{len(pairs)}` / `{len(pairs) * 2}`",
                f"- Source Bank `{SOURCE_CHR_BANK}` is preserved; cloned page: Bank `{TARGET_CHR_BANK}`",
                f"- Static normal mapper R1: `3E -> {STATIC_R1:02X}`",
                f"- Candidate MD5: `{payload['candidate']['patched_md5']}`",
                "",
                "This candidate keeps the original Bank 7 background/font page intact.",
                "The expanded Korean glyphs are written only to the cloned runtime page.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"ips={ips_path}")
    print(f"rom={rom_path}")
    print(f"patched_md5={payload['candidate']['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

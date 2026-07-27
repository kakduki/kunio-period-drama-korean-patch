#!/usr/bin/env python3
"""Build the tier-2 Korean opening candidate with the static R1 page."""

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
from build_opening_dialogue_16x16_proof import build_square_glyph_tiles, default_square_font
from build_opening_dialogue_proof import BASE_MD5, resolve_base_rom
from build_patch import make_records, write_ips
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


SOURCE_CHR_BANK = 7
TARGET_CHR_BANK = 8
CHR_BANK_SIZE = 0x2000
MAPPER_SETUP_ROM_OFFSET = 0x1EE57
MAPPER_SETUP_ORIGINAL = bytes.fromhex("A9 3C 8D 02 05 A9 3E 8D 03 05")
STATIC_R1 = 0x46
OUT_STEM = "kunio_period_drama_korean_opening_bank8_static_r1_capacity_tier2"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_dialogue_bank8_static_r1_capacity_tier2"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_capacity_tier2.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_capacity_tier2.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_capacity_tier2_font_preview.png"


def apply_candidate(base: bytes, config: dict[str, object], font_path: Path) -> tuple[bytes, list[dict[str, object]]]:
    profile = config["profile"]
    assert isinstance(profile, dict)
    pairs = profile["glyph_code_pairs"]
    assert isinstance(pairs, dict)
    patched, targets = apply_capacity_candidate(
        base,
        build_square_glyph_tiles(font_path, pairs),
        config,
    )
    layout = parse_ines_layout(base)
    source_start = layout.chr_start + SOURCE_CHR_BANK * CHR_BANK_SIZE
    target_start = layout.chr_start + TARGET_CHR_BANK * CHR_BANK_SIZE
    expanded = bytearray(patched)
    expanded[target_start : target_start + CHR_BANK_SIZE] = patched[source_start : source_start + CHR_BANK_SIZE]
    targets.append(
        {
            "kind": "chr_page_clone_from_patched_source",
            "rom_offset": target_start,
            "length": CHR_BANK_SIZE,
            "source_chr_bank": SOURCE_CHR_BANK,
            "target_chr_bank": TARGET_CHR_BANK,
        }
    )
    r1_immediate = MAPPER_SETUP_ROM_OFFSET + 6
    if base[r1_immediate] != 0x3E:
        raise ValueError("normal mapper R1 immediate does not match 0x3E")
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
        "status": "CANDIDATE_BUILT_PENDING_STATIC_R1_CAPACITY_PROOF",
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
                "# Opening Bank 8 Static R1 Tier-2 Capacity Proof",
                "",
                f"Status: {payload['status']}",
                "",
                f"- Base MD5: `{actual_md5}`",
                f"- Pointer `{record['pointer_index']}` record: `{record['record_rom_offset']}`, `{len(config['encoded'])}` bytes",
                f"- Korean glyphs/source pairs: `{len(pairs)}` / `{len(pairs) * 2}`",
                f"- CHR clone: Bank `{SOURCE_CHR_BANK}` -> Bank `{TARGET_CHR_BANK}`",
                f"- Static normal mapper R1: `3E -> {STATIC_R1:02X}`",
                f"- Candidate MD5: `{payload['candidate']['patched_md5']}`",
                "",
                "This candidate preserves the original fixed mapper routine and",
                "uses the game's normal R1 setup lifecycle. The tier-2 Korean source",
                "record is copied into the cloned page before bounded runtime proof.",
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

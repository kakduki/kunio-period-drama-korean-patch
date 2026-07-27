#!/usr/bin/env python3
"""Build a bounded opening proof using the game's normal R1 mapper setup."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_opening_dialogue_16x16_proof import build_square_glyph_tiles, default_square_font
from build_opening_dialogue_8x16_proof import CODE_CAVE_ROM_OFFSET
from build_opening_dialogue_bank8_page_switch_proof import (
    PAGE_GLYPH_CODE_PAIRS,
    PAGE_SWITCH_RECORD,
    apply_page_switch_candidate,
)
from build_opening_dialogue_proof import BASE_MD5, resolve_base_rom
from build_patch import make_records, write_ips
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


MAPPER_SETUP_ROM_OFFSET = 0x1EE57
MAPPER_SETUP_ORIGINAL = bytes.fromhex("A9 3C 8D 02 05 A9 3E 8D 03 05")
SOURCE_PAGE_SEQUENCE = bytes.fromhex("A9 40 8D 02 05 A9 42 8D 03 05")
STATIC_R1 = 0x46
OUT_STEM = "kunio_period_drama_korean_opening_bank8_static_r1_page_proof"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "opening_dialogue_bank8_static_r1_page_proof"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_page_proof.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_page_proof.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_bank8_static_r1_page_proof_font_preview.png"


def apply_static_r1_candidate(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
) -> tuple[bytes, list[dict[str, object]]]:
    if base[MAPPER_SETUP_ROM_OFFSET : MAPPER_SETUP_ROM_OFFSET + len(MAPPER_SETUP_ORIGINAL)] != MAPPER_SETUP_ORIGINAL:
        raise ValueError("normal mapper setup does not match the verified base ROM")

    patched, targets = apply_page_switch_candidate(base, glyph_tiles)
    patched = bytearray(patched)
    cave_start = CODE_CAVE_ROM_OFFSET
    helper = bytes(patched[cave_start : cave_start + 75])
    if helper.count(SOURCE_PAGE_SEQUENCE) != 1:
        raise ValueError("renderer helper page-write sequence is not unique")
    patched[cave_start : cave_start + 75] = helper.replace(SOURCE_PAGE_SEQUENCE, b"\xEA" * 10)

    r1_immediate = MAPPER_SETUP_ROM_OFFSET + 6
    patched[r1_immediate] = STATIC_R1
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
        for offset, (old, new) in enumerate(zip(base, patched))
        if old != new and not any(start <= offset < end for start, end in allowed)
    ]
    if escaped:
        raise AssertionError(f"candidate changed bytes outside declared targets: {escaped[:8]}")
    return bytes(patched), targets


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
    patched, targets = apply_static_r1_candidate(base, glyph_tiles)
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

    payload = {
        "status": "CANDIDATE_BUILT_PENDING_STATIC_R1_PROOF",
        "source": {
            "base_md5": actual_md5,
            "mapper_setup_rom_offset": f"0x{MAPPER_SETUP_ROM_OFFSET:05X}",
            "mapper_setup_cpu": "0xEE47",
            "static_r1": f"0x{STATIC_R1:02X}",
            "font_page": 8,
            "glyph_code_pairs": {
                glyph: [f"0x{left:02X}", f"0x{right:02X}"]
                for glyph, (left, right) in PAGE_GLYPH_CODE_PAIRS.items()
            },
            "record_hex": PAGE_SWITCH_RECORD.hex(" "),
        },
        "candidate": {
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": str(ips_path.relative_to(REPO_ROOT)),
            "rom_path": str(rom_path.relative_to(REPO_ROOT)),
            "ips_record_count": len(records),
            "targets": targets,
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(
        "\n".join(
            [
                "# Opening Bank 8 Static R1 Page Proof",
                "",
                f"Status: {payload['status']}",
                "",
                f"- Base MD5: {actual_md5}",
                f"- Normal mapper setup: ROM `0x{MAPPER_SETUP_ROM_OFFSET:05X}` / CPU `$EE47`",
                f"- R1 replacement: `3E -> {STATIC_R1:02X}`",
                f"- Candidate MD5: {payload['candidate']['patched_md5']}",
                "",
                "The candidate keeps the original fixed mapper routine and changes",
                "one normal setup value. The renderer-side transient page write is",
                "disabled so the runtime result tests only the static R1 lifecycle.",
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

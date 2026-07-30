#!/usr/bin/env python3
"""Probe disjoint Korean source-code ranges on appended CHR Bank 16."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_opening_dialogue_16x16_proof import build_square_glyph_tiles, default_square_font
from build_opening_dialogue_8x16_proof import CODE_CAVE_ROM_OFFSET, CODE_CAVE_SIZE
from build_patch import make_records, write_ips
from build_ptr181_bank8_page_probe import (
    CHR_BANK_SIZE,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    resolve_base_rom,
)
from build_ptr181_expanded_chr_probe import (
    DEFAULT_PREVIEW,
    SOURCE_CHR_BANK,
    patch_expanded_chr,
)
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


PROBE_GLYPH_PAIRS = {
    "한": (0x81, 0x82),
    "글": (0x89, 0x8A),
    "확": (0x8B, 0x8C),
    "장": (0x9E, 0x9F),
    "코": (0xC0, 0xC1),
    "드": (0xC7, 0xC8),
    "검": (0xCB, 0xCC),
    "증": (0xDE, 0xDF),
}
PROBE_RECORD_PREFIX = bytes(
    code for pair in PROBE_GLYPH_PAIRS.values() for code in pair
) + bytes.fromhex("CA 00 FF")
PROBE_RECORD = PROBE_RECORD_PREFIX + b"\x00" * (
    RECORD_LENGTH - len(PROBE_RECORD_PREFIX)
)
HELPER_OLD_END = bytes.fromhex("C9 CA B0")
HELPER_NEW_END = bytes.fromhex("C9 E0 B0")
OUT_STEM = "kunio_period_drama_korean_ptr181_expanded_code_pool_probe"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "ptr181_expanded_code_pool_probe"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "ptr181_expanded_code_pool_probe.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "ptr181_expanded_code_pool_probe.md"
DEFAULT_CODE_PREVIEW = REPO_ROOT / "rom_analysis" / "ptr181_expanded_code_pool_probe_font_preview.png"


def patch_code_pool(base: bytes, font_path: Path) -> bytes:
    patched = bytearray(patch_expanded_chr(base, font_path))
    helper = bytes(
        patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE]
    )
    if helper.count(HELPER_OLD_END) != 2:
        raise AssertionError("paired renderer end comparisons changed")
    helper = helper.replace(HELPER_OLD_END, HELPER_NEW_END)
    patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE] = helper

    source_start = 0x20010 + SOURCE_CHR_BANK * CHR_BANK_SIZE
    new_bank_start = len(base)
    patched[new_bank_start:new_bank_start + CHR_BANK_SIZE] = base[
        source_start:source_start + CHR_BANK_SIZE
    ]
    glyph_tiles = build_square_glyph_tiles(font_path, PROBE_GLYPH_PAIRS)
    for glyph, pair in PROBE_GLYPH_PAIRS.items():
        for tile_index, code in enumerate(
            (pair[0], pair[1], pair[0] + 0x20, pair[1] + 0x20)
        ):
            offset = new_bank_start + (0x100 + code) * 16
            patched[offset:offset + 16] = glyph_tiles[glyph][tile_index]
    patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = PROBE_RECORD
    return bytes(patched)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?")
    parser.add_argument("--font", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    base = resolve_base_rom(args.rom).read_bytes()
    font = default_square_font(args.font)
    patched = patch_code_pool(base, font)
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    if apply_ips(base, ips_path) != patched:
        raise AssertionError("expanded code-pool IPS round trip failed")
    write_square_preview(
        list(PROBE_GLYPH_PAIRS),
        DEFAULT_CODE_PREVIEW,
        font_path=font,
        target_pixels=15,
        threshold=100,
    )
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_EXPANDED_CODE_POOL_RUNTIME_PROOF",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(patched).hexdigest(),
        "display_text": "".join(PROBE_GLYPH_PAIRS),
        "source_code_pairs": {
            glyph: [f"0x{left:02X}", f"0x{right:02X}"]
            for glyph, (left, right) in PROBE_GLYPH_PAIRS.items()
        },
        "renderer_source_ranges": ["0x81-0x9F", "0xC0-0xDF except 0xCA"],
        "candidate_size": len(patched),
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
    }
    DEFAULT_REPORT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    DEFAULT_REPORT_MARKDOWN.write_text(
        "\n".join(
            [
                "# PTR-181 Expanded Code-Pool Probe",
                "",
                f"Status: **{payload['status']}**",
                "",
                f"- Candidate MD5: `{payload['candidate_md5']}`",
                f"- Display text: `{payload['display_text']}`",
                "- Source boundaries sampled: `81/82`, `89/8A`, `8B/8C`, `9E/9F`, `C0/C1`, `C7/C8`, `CB/CC`, `DE/DF`",
                "- Appended CHR mapping: `R1=86`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"rom={rom_path}")
    print(f"candidate_md5={payload['candidate_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

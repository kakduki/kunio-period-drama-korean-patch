#!/usr/bin/env python3
"""Build a semantic PTR-181 Korean 8x16 candidate on appended CHR."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_opening_dialogue_8x16_proof import default_tall_font
from build_patch import make_records, write_ips
from build_ptr181_bank8_page_probe import (
    CHR_BANK_SIZE,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    resolve_base_rom,
)
from build_ptr181_expanded_chr_probe import SOURCE_CHR_BANK, patch_expanded_chr
from korean_tile_font import render_tall_tiles, write_tall_preview
from rom_utils import REPO_ROOT


GLYPH_CODES = {
    "츠": 0x81,
    "우": 0x82,
    "형": 0x83,
    "님": 0x84,
    "기": 0x85,
    "다": 0x86,
    "려": 0x87,
}
KOREAN_TEXT = "츠우: 형님 / 기다려!"
RECORD_PREFIX = bytes.fromhex(
    "81 82 BB 00 83 84 CA 00 85 86 87 CA FF"
)
KOREAN_RECORD = RECORD_PREFIX + b"\x00" * (RECORD_LENGTH - len(RECORD_PREFIX))
OUT_STEM = "kunio_period_drama_korean_ptr181_semantic_8x16"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "ptr181_korean_8x16_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "ptr181_korean_8x16_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "ptr181_korean_8x16_candidate.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "ptr181_korean_8x16_candidate_font_preview.png"


def patch_korean_8x16(base: bytes, font_path: Path) -> bytes:
    patched = bytearray(patch_expanded_chr(base, font_path))
    source_start = 0x20010 + SOURCE_CHR_BANK * CHR_BANK_SIZE
    new_bank_start = len(base)
    patched[new_bank_start:new_bank_start + CHR_BANK_SIZE] = base[
        source_start:source_start + CHR_BANK_SIZE
    ]
    for glyph, code in GLYPH_CODES.items():
        top, bottom = render_tall_tiles(glyph, font_path=font_path, threshold=92)
        top_offset = new_bank_start + (0x100 + code) * 16
        bottom_offset = new_bank_start + (0x100 + code + 0x20) * 16
        patched[top_offset:top_offset + 16] = top
        patched[bottom_offset:bottom_offset + 16] = bottom
    patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = KOREAN_RECORD
    return bytes(patched)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?")
    parser.add_argument("--font", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    base = resolve_base_rom(args.rom).read_bytes()
    font = default_tall_font(args.font)
    patched = patch_korean_8x16(base, font)
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    if apply_ips(base, ips_path) != patched:
        raise AssertionError("8x16 semantic IPS round trip failed")
    write_tall_preview(GLYPH_CODES, DEFAULT_PREVIEW, font_path=font)
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_8X16_READABILITY_PROOF",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(patched).hexdigest(),
        "pointer_index": 181,
        "korean_text": KOREAN_TEXT,
        "translation_basis": "English pointer structure plus Japanese-context review required",
        "font_profile": "one_source_code_per_8x16_hangul_syllable",
        "glyph_codes": {glyph: f"0x{code:02X}" for glyph, code in GLYPH_CODES.items()},
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
    }
    DEFAULT_REPORT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    DEFAULT_REPORT_MARKDOWN.write_text(
        "\n".join(
            [
                "# PTR-181 Korean 8x16 Candidate",
                "",
                f"Status: **{payload['status']}**",
                "",
                f"- Korean text: `{KOREAN_TEXT}`",
                f"- Candidate MD5: `{payload['candidate_md5']}`",
                "- One source code per Hangul syllable",
                "- Appended CHR Bank 16, scene-scoped `R1=86` with automatic restore",
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

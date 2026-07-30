#!/usr/bin/env python3
"""Move the proven PTR-181 Korean page into newly appended CHR ROM."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from apply_ips_standalone import apply_ips
from build_opening_dialogue_16x16_proof import (
    PAIR_GLYPH_CODES,
    build_square_glyph_tiles,
    default_square_font,
)
from build_patch import make_records, write_ips
from build_ptr181_bank8_page_probe import BASE_MD5, CHR_BANK_SIZE, resolve_base_rom
from build_ptr181_conditional_mapper_probe import (
    MAPPER_SELECT_CAVE_ROM_OFFSET,
    patch_candidate,
)
from korean_tile_font import write_square_preview
from rom_utils import REPO_ROOT


ORIGINAL_CHR_BANKS = 16
EXPANDED_CHR_BANKS = 17
SOURCE_CHR_BANK = 7
EXPANDED_CHR_BANK = 16
PHYSICAL_TILE_BASE = 0x100
EXPANDED_R1 = 0x86
TARGET_R1_PATTERN = bytes.fromhex("A9 3C 8D 02 05 A9 46")
OUT_STEM = "kunio_period_drama_korean_ptr181_expanded_chr_probe"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "ptr181_expanded_chr_probe"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "ptr181_expanded_chr_probe.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "ptr181_expanded_chr_probe.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "ptr181_expanded_chr_probe_font_preview.png"


def patch_expanded_chr(base: bytes, font_path: Path) -> bytes:
    if hashlib.md5(base).hexdigest() != BASE_MD5:
        raise ValueError("unsupported base ROM")
    layout = parse_ines_layout(base)
    if base[5] != ORIGINAL_CHR_BANKS or layout.chr_end != len(base):
        raise ValueError("base ROM is not the verified 16-bank CHR layout")

    conditional, _ = patch_candidate(base, font_path)
    patched = bytearray(conditional)
    # Undo the experimental overwrite of existing CHR Bank 8. The scalable
    # candidate owns only newly appended CHR bytes.
    patched[layout.chr_start:layout.chr_end] = base[layout.chr_start:layout.chr_end]
    patched[5] = EXPANDED_CHR_BANKS

    source_start = layout.chr_start + SOURCE_CHR_BANK * CHR_BANK_SIZE
    new_bank = bytearray(base[source_start:source_start + CHR_BANK_SIZE])
    glyph_tiles = build_square_glyph_tiles(font_path, PAIR_GLYPH_CODES)
    for glyph, pair in PAIR_GLYPH_CODES.items():
        for tile_index, code in enumerate(
            (pair[0], pair[1], pair[0] + 0x20, pair[1] + 0x20)
        ):
            physical_tile = PHYSICAL_TILE_BASE + code
            offset = physical_tile * 16
            new_bank[offset:offset + 16] = glyph_tiles[glyph][tile_index]
    patched.extend(new_bank)

    select = patched[
        MAPPER_SELECT_CAVE_ROM_OFFSET:MAPPER_SELECT_CAVE_ROM_OFFSET + 28
    ]
    offset = bytes(select).find(TARGET_R1_PATTERN)
    if offset < 0:
        raise AssertionError("conditional mapper target mapping not found")
    r1_offset = MAPPER_SELECT_CAVE_ROM_OFFSET + offset + len(TARGET_R1_PATTERN) - 1
    patched[r1_offset] = EXPANDED_R1

    if patched[layout.chr_start:layout.chr_end] != base[layout.chr_start:layout.chr_end]:
        raise AssertionError("expanded candidate modified an original CHR bank")
    if len(patched) != len(base) + CHR_BANK_SIZE:
        raise AssertionError("expanded candidate must append exactly one CHR bank")
    return bytes(patched)


def render_report(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "# PTR-181 Expanded CHR Probe",
            "",
            f"Status: **{payload['status']}**",
            "",
            f"- Base MD5: `{payload['base_md5']}`",
            f"- Candidate MD5: `{payload['candidate_md5']}`",
            "- CHR banks: `16 -> 17` (one appended 8 KiB bank)",
            "- Korean page: appended CHR Bank 16, MMC3 `R1=86`",
            "- Existing CHR banks: byte-identical to the base ROM",
            "",
            "This probe verifies scalable CHR expansion before multiple Korean pages",
            "are compiled. It is not a release candidate.",
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
    font = default_square_font(args.font)
    patched = patch_expanded_chr(base, font)
    records = make_records(base, patched)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)
    if apply_ips(base, ips_path) != patched:
        raise AssertionError("expanded IPS does not reproduce candidate ROM")
    write_square_preview(
        list(PAIR_GLYPH_CODES),
        DEFAULT_PREVIEW,
        font_path=font,
        target_pixels=15,
        threshold=100,
    )
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_EXPANDED_CHR_RUNTIME_PROOF",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(patched).hexdigest(),
        "base_size": len(base),
        "candidate_size": len(patched),
        "chr_banks_before": base[5],
        "chr_banks_after": patched[5],
        "expanded_chr_bank": EXPANDED_CHR_BANK,
        "expanded_r1": f"0x{EXPANDED_R1:02X}",
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
        "ips_record_count": len(records),
    }
    DEFAULT_REPORT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    DEFAULT_REPORT_MARKDOWN.write_text(render_report(payload), encoding="utf-8")
    print(f"rom={rom_path}")
    print(f"candidate_md5={payload['candidate_md5']}")
    print(f"size={len(base)}->{len(patched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

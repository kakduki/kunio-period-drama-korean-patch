#!/usr/bin/env python3
"""Build a focused Korean name-table renderer proof candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_patch import make_records, write_ips
from korean_tile_font import find_korean_font, render_tile
from rom_utils import REPO_ROOT


SOURCE_OFFSET = 0x3FB32
SOURCE_EXPECTED = bytes.fromhex("88 96 9F 8B")
SOURCE_CODES = bytes((0x81, 0x82, 0x81, 0x82))
TEST_GLYPHS = ("다", "리", "다", "리")
CHR_BANK7_START = 0x2E010
CHR_TILE_BASE = 0x181
CHR_SLOT_START = CHR_BANK7_START + CHR_TILE_BASE * 0x10
DEFAULT_INPUT = REPO_ROOT / "output" / "full_nonpointer_korean_candidate" / "kunio_period_drama_korean_full_nonpointer_candidate.nes"
DEFAULT_OUT_DIR = REPO_ROOT / "output" / "name_table_korean_candidate"
OUT_STEM = "kunio_period_drama_korean_name_table_candidate"
REPORT_JSON = REPO_ROOT / "rom_analysis" / "name_table_korean_candidate.json"
REPORT_MD = REPO_ROOT / "rom_analysis" / "name_table_korean_candidate.md"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def build(input_rom: Path, out_dir: Path, font_path: str | None) -> dict[str, object]:
    original = input_rom.read_bytes()
    if original[SOURCE_OFFSET:SOURCE_OFFSET + len(SOURCE_EXPECTED)] != SOURCE_EXPECTED:
        raise ValueError(
            "input ROM does not contain the expected 0x3FB32 effective name-table source bytes"
        )

    patched = bytearray(original)
    patched[SOURCE_OFFSET:SOURCE_OFFSET + len(SOURCE_CODES)] = SOURCE_CODES
    glyph_rows: list[dict[str, object]] = []
    font = find_korean_font(font_path)
    for index, glyph in enumerate(TEST_GLYPHS):
        offset = CHR_SLOT_START + index * 0x10
        old = bytes(original[offset:offset + 0x10])
        new = render_tile(glyph, font_path=font, target_pixels=7, threshold=92)
        patched[offset:offset + 0x10] = new
        glyph_rows.append({
            "code": f"0x{SOURCE_CODES[index]:02X}",
            "glyph": glyph,
            "chr_rom_offset": f"0x{offset:05X}",
            "old_sha1_16": hashlib.sha1(old).hexdigest()[:16],
            "new_sha1_16": hashlib.sha1(new).hexdigest()[:16],
        })

    patched_bytes = bytes(patched)
    out_dir.mkdir(parents=True, exist_ok=True)
    rom_path = out_dir / f"{OUT_STEM}.nes"
    ips_path = out_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(patched_bytes)
    records = make_records(original, patched_bytes)
    write_ips(ips_path, records)
    if apply_ips(original, ips_path) != patched_bytes:
        raise AssertionError("name-table candidate IPS round trip failed")

    payload: dict[str, object] = {
        "status": "SOFT_GATE_PASS_ONE_CONTEXT",
        "input_rom": str(input_rom),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "input_md5": md5(original),
        "candidate_md5": md5(patched_bytes),
        "source_rom_offset": f"0x{SOURCE_OFFSET:05X}",
        "source_expected_bytes": SOURCE_EXPECTED.hex(" ").upper(),
        "source_test_bytes": SOURCE_CODES.hex(" ").upper(),
        "source_test_text": "".join(TEST_GLYPHS),
        "ppu_target_range": "0x2043-0x2046",
        "ppu_expected_sequence": SOURCE_EXPECTED.hex(" ").upper(),
        "ppu_test_sequence": SOURCE_CODES.hex(" ").upper(),
        "mapper_contract": {
            "ppu_control": "0x88",
            "mmc3_r1": "0x3E",
            "physical_chr_8k_bank": 7,
            "physical_tile_formula": "0x100 + tile_code",
        },
        "chr_slot_start": f"0x{CHR_SLOT_START:05X}",
        "glyph_rows": glyph_rows,
        "ips_records": len(records),
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Name-Table Korean Candidate",
        "",
        "Focused soft-gate proof candidate for the renderer family used by the effective name-table source table.",
        "",
        f"- Input candidate: {input_rom}",
        f"- Candidate ROM: {rom_path}",
        f"- Candidate IPS: {ips_path}",
        f"- Input MD5: {payload['input_md5']}",
        f"- Candidate MD5: {payload['candidate_md5']}",
        f"- Source ROM range: {payload['source_rom_offset']}",
        f"- Source bytes: {payload['source_expected_bytes']} -> {payload['source_test_bytes']}",
        f"- Test text: {payload['source_test_text']}",
        f"- Expected PPU target: {payload['ppu_target_range']}",
        f"- PPU sequence: {payload['ppu_expected_sequence']} -> {payload['ppu_test_sequence']}",
        "- Runtime contract: PPUCTRL 0x88, MMC3 R1 0x3E, physical CHR Bank 7, tile 0x100 + code.",
        "- Source-owner probe result: physical ROM offset 0x3FB32; 0x0561B was not active on this route.",
        "",
        "## Scope",
        "",
        "- This candidate changes only one visible four-byte source record and four CHR glyph slots.",
        "- The text is intentionally a bounded test string; it is not a release translation.",
        "- PASS requires the PPU trace to show 81 82 81 82 at 0x2043-0x2046 and the screenshot to show the Korean glyphs.",
        "- Runtime source and screenshot proof are recorded for one context; release status remains NOT_READY.",
        "",
        "## Glyph Slots",
        "",
        "| code | glyph | CHR ROM offset |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| {row['code']} | {row['glyph']} | {row['chr_rom_offset']} |" for row in glyph_rows)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-rom", default=str(DEFAULT_INPUT))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--font")
    args = parser.parse_args()
    payload = build(
        Path(args.input_rom).expanduser().resolve(),
        Path(args.out_dir).expanduser().resolve(),
        args.font,
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

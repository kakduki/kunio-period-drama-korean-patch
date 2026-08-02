#!/usr/bin/env python3
"""Build the next bounded Korean Items candidate from the English owner chain.

This candidate follows the English patch's actual runtime owners:

* the five-byte player name seed at ROM+0x00561B;
* the title suffix at ROM+0x136F4, which expands the name through control B6;
* the empty-inventory label at ROM+0x0FC31.

It preserves the existing action candidate and only adds these source records
plus eight low-code R0 glyph tiles.  The renderer accepts high input codes in
the name/title source and masks them to low tile codes, so the same glyph pool
also serves the direct-low NONE row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ips, parse_ines_layout
from build_direct_low_korean_candidate import load_glyphs
from build_patch import (
    CHR_BANK7_START,
    CHR_TILE_SIZE,
    glyph_8x16_to_8x8_tile,
    make_records,
    write_ips,
)
from rom_utils import REPO_ROOT


DEFAULT_INPUT = (
    REPO_ROOT
    / "output"
    / "full_korean_items_action_candidate"
    / "kunio_period_drama_korean_full_items_action_candidate.nes"
)
DEFAULT_BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_items_title_none_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_items_title_none_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_items_title_none_candidate.md"
OUT_STEM = "kunio_period_drama_korean_full_items_title_none_candidate"

NAME_SOURCE_OFFSET = 0x00561B
NAME_SOURCE_LENGTH = 5
NAME_PPU_SOURCE_OFFSET = 0x3FB32
TITLE_SOURCE_OFFSET = 0x136F4
TITLE_SOURCE_LENGTH = 12
NONE_SOURCE_OFFSET = 0x0FC31
NONE_SOURCE_LENGTH = 5
KNOWN_DIRECT_LOW_NONE_BYTES = bytes([0x05, 0x00, 0x00, 0x00, 0x02])
ENGLISH_OWNER_BYTES = {
    "name_prg_seed": bytes([0x8B, 0x95, 0x8E, 0x89, 0x8F]),
    "name_ppu_seed": bytes([0x8B, 0x95, 0x8E, 0x89, 0x8F]),
    "title_suffix": bytes([0xB6, 0x93, 0x80, 0x89, 0x94, 0x85, 0x8D, 0x93, 0x80, 0x80, 0x80, 0xCD]),
    "none": bytes([0x0E, 0x0F, 0x0E, 0x05, 0x38]),
}

GLYPH_CODES = {
    "쿠": 0x20,
    "니": 0x21,
    "오": 0x22,
    "의": 0x23,
    "물": 0x24,
    "건": 0x25,
    "없": 0x26,
    "음": 0x27,
}
INPUT_CODES = {character: code + 0x80 for character, code in GLYPH_CODES.items()}
NAME_BYTES = bytes([INPUT_CODES["쿠"], INPUT_CODES["니"], INPUT_CODES["오"], 0xFF, 0xFF])
NAME_PPU_BYTES = bytes([INPUT_CODES["쿠"], INPUT_CODES["니"], INPUT_CODES["오"], 0x80, 0x80])
TITLE_BYTES = bytes(
    [
        0xB6,
        INPUT_CODES["의"],
        0x80,
        INPUT_CODES["물"],
        INPUT_CODES["건"],
        0x80,
        0x80,
        0x80,
        0x80,
        0x80,
        0x80,
        0xCD,
    ]
)
NONE_BYTES = bytes([GLYPH_CODES["없"], GLYPH_CODES["음"], 0x38, 0x38, 0x38])


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def tile_offset(layout, low_code: int) -> int:
    if not 0x20 <= low_code <= 0x27:
        raise ValueError(f"unexpected R0 low code: 0x{low_code:02X}")
    return layout.chr_start + 0x7 * 0x2000 + (0x100 + low_code) * CHR_TILE_SIZE


def hex_bytes(data: bytes) -> str:
    return data.hex(" ").upper()


def build(
    input_rom: Path,
    base_rom: Path,
    char_map: Path,
    font_bin: Path,
    output_dir: Path,
    report_json: Path,
    report_markdown: Path,
    runtime_report: Path | None = None,
) -> dict[str, object]:
    base = base_rom.read_bytes()
    current = input_rom.read_bytes()
    if len(current) < len(base):
        raise ValueError("input candidate is shorter than the verified base ROM")
    layout = parse_ines_layout(base)
    glyphs = load_glyphs(char_map, font_bin)
    missing = sorted(set(GLYPH_CODES) - set(glyphs))
    if missing:
        raise ValueError(f"font is missing title/NONE glyphs: {missing}")

    runtime_pass = False
    if runtime_report is not None:
        if not runtime_report.exists():
            raise FileNotFoundError(f"Items title/NONE runtime report not found: {runtime_report}")
        runtime_pass = json.loads(runtime_report.read_text(encoding="utf-8")).get("runtime_byte_gate") is True
    runtime_gate = "PASS_BYTE_PROOF" if runtime_pass else "PENDING_FCEUX_BYTE_PROOF"
    runtime_note = "PASS" if runtime_pass else "pending bounded runtime capture"
    source_specs = {
        "name_prg_seed": (NAME_SOURCE_OFFSET, NAME_SOURCE_LENGTH, NAME_BYTES),
        "name_ppu_seed": (NAME_PPU_SOURCE_OFFSET, NAME_SOURCE_LENGTH, NAME_PPU_BYTES),
        "title_suffix": (TITLE_SOURCE_OFFSET, TITLE_SOURCE_LENGTH, TITLE_BYTES),
        "none": (NONE_SOURCE_OFFSET, NONE_SOURCE_LENGTH, NONE_BYTES),
    }
    patched = bytearray(current)
    source_rows: list[dict[str, object]] = []
    for owner, (offset, length, replacement) in source_specs.items():
        base_bytes = base[offset : offset + length]
        current_bytes = current[offset : offset + length]
        if len(base_bytes) != length or len(current_bytes) != length:
            raise ValueError(f"short source record for {owner} at 0x{offset:05X}")
        allowed_input_bytes = {base_bytes}
        english_bytes = ENGLISH_OWNER_BYTES.get(owner)
        if english_bytes is not None:
            allowed_input_bytes.add(english_bytes)
        if owner == "none":
            # The current action candidate is composed on top of the earlier
            # direct-low candidate, which used this bounded intermediate row.
            allowed_input_bytes.add(KNOWN_DIRECT_LOW_NONE_BYTES)
        if current_bytes not in allowed_input_bytes:
            raise ValueError(
                f"input candidate drift at 0x{offset:05X}: "
                f"{hex_bytes(current_bytes)} != base {hex_bytes(base_bytes)}"
            )
        patched[offset : offset + length] = replacement
        source_rows.append(
            {
                "owner": owner,
                "rom_offset": f"0x{offset:05X}",
                "length": length,
                "base_bytes": hex_bytes(base_bytes),
                "input_bytes": hex_bytes(current_bytes),
                "new_bytes": hex_bytes(replacement),
            }
        )

    glyph_rows: list[dict[str, object]] = []
    for character, low_code in GLYPH_CODES.items():
        offset = tile_offset(layout, low_code)
        tile = glyph_8x16_to_8x8_tile(glyphs[character])
        patched[offset : offset + CHR_TILE_SIZE] = tile
        glyph_rows.append(
            {
                "character": character,
                "low_code": f"0x{low_code:02X}",
                "rom_offset": f"0x{offset:05X}",
                "tile_bytes": hex_bytes(tile),
            }
        )

    candidate = bytes(patched)
    allowed_ranges = [
        (offset, offset + length)
        for offset, length, _ in source_specs.values()
    ] + [
        (tile_offset(layout, low_code), tile_offset(layout, low_code) + CHR_TILE_SIZE)
        for low_code in GLYPH_CODES.values()
    ]
    unexpected: list[int] = []
    for offset, (before, after) in enumerate(zip(current, candidate)):
        if before == after:
            continue
        if not any(start <= offset < stop for start, stop in allowed_ranges):
            unexpected.append(offset)
    if unexpected:
        raise AssertionError(f"unexpected input-relative changes: {unexpected[:8]}")

    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"{OUT_STEM}.nes"
    ips_path = output_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(candidate)
    records = make_records(base, candidate)
    write_ips(ips_path, records)
    round_trip = apply_records(base, *parse_ips(ips_path.read_bytes()))
    if round_trip != candidate:
        raise AssertionError("IPS round trip differs from candidate ROM")

    payload: dict[str, object] = {
        "status": "BUILT_ITEMS_TITLE_NONE_RUNTIME_BYTE_PASS_VISUAL_UNKNOWN" if runtime_pass else "BUILT_ITEMS_TITLE_NONE_STATIC_PASS_RUNTIME_PENDING",
        "release_status": "NOT_READY",
        "base_md5": md5(base),
        "input_md5": md5(current),
        "candidate_md5": md5(candidate),
        "input_rom": str(input_rom),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "source_chains": {
            "name": "PRG 0x00561B + CHR 0x3FB32 -> PPU read -> RAM $7AFB -> title prefix RAM $60A8 -> PPU Items row 5",
            "title_suffix": "ROM 0x136F4 -> title suffix RAM $60AD -> PPU Items row 5",
            "none": "ROM 0x0FC31 -> RAM $6506 -> PPU Items row 8",
        },
        "source_rows": source_rows,
        "glyph_rows": glyph_rows,
        "font_pages": "CHR Bank 7 R0, low tiles 0x120-0x127; normal Items R1 remains 0x3E/0x3F",
        "ips_record_count": len(records),
        "runtime_gate": runtime_gate,
        "visual_gate": "UNKNOWN_NATIVE_GDSCREENSHOT_TRANSPARENT",
        "notes": [
            "The English owner chain is preserved; only the three source records and eight R0 glyph tiles are added relative to the action candidate.",
            "Input codes 0xA0-0xA7 mask to low R0 tile codes 0x20-0x27 in the fixed-bank text parser.",
            "Runtime title/NONE byte proof passed on the bounded menu route." if runtime_pass else "Runtime proof must verify title row 5 and NONE row 8 on the same bounded menu route before release consideration.",
        ],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Full Korean Items Title and NONE Candidate",
        "",
        f"- Status: `{payload['status']}`.",
        "- Release status: `NOT_READY`.",
        f"- Base MD5: `{payload['base_md5']}`.",
        f"- Input action-candidate MD5: `{payload['input_md5']}`.",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        "- Runtime route: bounded Items menu capture at frame 1906; no opening-loop claim.",
        "",
        "## English Owner Chains",
        "",
        "| owner | source | runtime destination | new bytes |",
        "| --- | --- | --- | --- |",
    ]
    for row in source_rows:
        destination = {
            "name_prg_seed": "alternate PRG name seed",
            "name_ppu_seed": "PPU-read name seed -> RAM $7AFB -> title prefix $60A8",
            "title_suffix": "RAM $60AD",
            "none": "RAM $6506",
        }[str(row["owner"])]
        lines.append(
            f"| {row['owner']} | `{row['rom_offset']}` | {destination} | `{row['new_bytes']}` |"
        )
    lines += [
        "",
        "## Gate",
        "",
        "- Static source scope: PASS.",
        "- IPS round trip: PASS.",
        f"- FCEUX title/NONE byte proof: {runtime_note}.",
        "- Native Lua screenshot pixels: UNKNOWN because the available screenshot buffer is transparent.",
        "- Release status: NOT_READY.",
    ]
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-rom", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--font-bin", type=Path, default=DEFAULT_FONT_BIN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--runtime-report", type=Path, help="Optional bounded title/NONE runtime verifier JSON report.")
    args = parser.parse_args()
    payload = build(
        args.input_rom.resolve(),
        args.base_rom.resolve(),
        args.char_map.resolve(),
        args.font_bin.resolve(),
        args.out_dir.resolve(),
        args.report_json.resolve(),
        args.report_markdown.resolve(),
        args.runtime_report.resolve() if args.runtime_report else None,
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

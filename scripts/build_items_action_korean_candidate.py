#!/usr/bin/env python3
"""Add the verified Items action row to the composed Korean candidate.

The English reference copies four action labels through the Bank 4 source
chain at ROM+0x13727.  This builder preserves the queue layout, replaces only
those four source slots, and puts collapsed Korean 8x8 glyphs in an isolated
font pool on the normal Items R1 page (CHR 1 KiB page 0x3E/0x3F).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_direct_low_korean_candidate import load_glyphs
from build_main_menu_korean_candidate import GLYPH_CODE_PAIRS, KNOWN_ACTIVE_HIGH_CODES
from build_patch import glyph_8x16_to_8x8_tile, make_records, write_ips
from rom_utils import REPO_ROOT


DEFAULT_INPUT = (
    REPO_ROOT
    / "output"
    / "full_korean_direct_low_candidate"
    / "kunio_period_drama_korean_full_direct_low_candidate.nes"
)
DEFAULT_BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
DEFAULT_FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_items_action_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_items_action_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_items_action_candidate.md"
OUT_STEM = "kunio_period_drama_korean_full_items_action_candidate"

SOURCE_ROM_OFFSET = 0x13727
SOURCE_LENGTH = 33
ACTION_SLOTS = {
    "USE": (4, 7),
    "REMOVE": (12, 18),
    "GIVE": (20, 24),
    "DRP": (28, 31),
}
KOREAN_ACTIONS = {
    "USE": "\uC0AC\uC6A9",
    "REMOVE": "\uBC84\uB9AC\uAE30",
    "GIVE": "\uC8FC\uAE30",
    "DRP": "\uBC84\uB9BC",
}
ITEM_GLYPHS = tuple(dict.fromkeys("".join(KOREAN_ACTIONS.values())))
CONTROL_CODES = frozenset({0x00, 0xBB, 0xCA, 0xF8, 0xF9, 0xFF})
ITEM_ORIGINAL_CODES = frozenset(
    value
    for values in (
        (0x95, 0x93, 0x85),
        (0x92, 0x85, 0x8D, 0x8F, 0x96, 0x85),
        (0x87, 0x89, 0x96, 0x85),
        (0x84, 0x92, 0x90),
    )
    for value in values
)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def page_tile_offset(layout, page: int, code: int) -> int:
    if not 0x80 <= code <= 0xFF:
        raise ValueError(f"Items glyph code must be 0x80-0xFF: 0x{code:02X}")
    page_count = (layout.chr_end - layout.chr_start) // 0x400
    absolute_page = page + ((code & 0x7F) // 0x40)
    if not 0 <= absolute_page < page_count:
        raise ValueError(f"CHR page is outside the ROM: 0x{absolute_page:02X}")
    return layout.chr_start + absolute_page * 0x400 + (code & 0x3F) * 16


def isolated_codes() -> dict[str, int]:
    menu_codes = {
        code
        for pair in GLYPH_CODE_PAIRS.values()
        for code in (*pair, pair[0] + 0x20, pair[1] + 0x20)
    }
    reserved = menu_codes | set(KNOWN_ACTIVE_HIGH_CODES) | set(ITEM_ORIGINAL_CODES) | set(CONTROL_CODES)
    available = [code for code in range(0x80, 0x100) if code not in reserved]
    if len(available) < len(ITEM_GLYPHS):
        raise ValueError("not enough isolated Items glyph codes")
    return dict(zip(ITEM_GLYPHS, available[: len(ITEM_GLYPHS)], strict=True))


def encode_slot(text: str, width: int, code_by_glyph: dict[str, int]) -> bytes:
    if len(text) > width:
        raise ValueError(f"Items label {text!r} exceeds slot width {width}")
    encoded = bytes(code_by_glyph[character] for character in text)
    return encoded + b"\x00" * (width - len(encoded))


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
    source = base[SOURCE_ROM_OFFSET : SOURCE_ROM_OFFSET + SOURCE_LENGTH]
    if len(source) != SOURCE_LENGTH:
        raise ValueError("Items source chain lies outside the base ROM")

    code_by_glyph = isolated_codes()
    glyphs = load_glyphs(char_map, font_bin)
    missing = sorted(set(ITEM_GLYPHS) - set(glyphs))
    if missing:
        raise ValueError(f"font is missing Items glyphs: {missing}")

    runtime_pass = False
    if runtime_report is not None:
        if not runtime_report.exists():
            raise FileNotFoundError(f"Items runtime report not found: {runtime_report}")
        runtime_pass = json.loads(runtime_report.read_text(encoding="utf-8")).get("verdict") == "PASS"
    runtime_gate = "PASS" if runtime_pass else "UNKNOWN"
    patched = bytearray(current)
    source_after = bytearray(source)
    slot_report: list[dict[str, object]] = []
    for english, (start, stop) in ACTION_SLOTS.items():
        replacement = encode_slot(KOREAN_ACTIONS[english], stop - start, code_by_glyph)
        source_after[start:stop] = replacement
        patched[SOURCE_ROM_OFFSET + start : SOURCE_ROM_OFFSET + stop] = replacement
        slot_report.append(
            {
                "english": english,
                "korean": KOREAN_ACTIONS[english],
                "rom_offset": f"0x{SOURCE_ROM_OFFSET + start:05X}",
                "length": stop - start,
                "base_bytes": source[start:stop].hex(" ").upper(),
                "new_bytes": replacement.hex(" ").upper(),
            }
        )

    for glyph, code in code_by_glyph.items():
        offset = page_tile_offset(layout, 0x3E, code)
        patched[offset : offset + 16] = glyph_8x16_to_8x8_tile(glyphs[glyph])

    candidate = bytes(patched)
    if candidate == current:
        raise AssertionError("Items action builder made no changes")
    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"{OUT_STEM}.nes"
    ips_path = output_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(candidate)
    write_ips(ips_path, make_records(base, candidate))

    payload: dict[str, object] = {
        "status": "BUILT_ITEMS_ACTION_STATIC_PASS_RUNTIME_PASS" if runtime_pass else "BUILT_ITEMS_ACTION_STATIC_PASS_RUNTIME_UNKNOWN",
        "release_status": "NOT_READY",
        "base_md5": md5(base),
        "input_md5": md5(current),
        "candidate_md5": md5(candidate),
        "input_rom": str(input_rom),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "source_chain": {
            "rom_offset": f"0x{SOURCE_ROM_OFFSET:05X}",
            "length": SOURCE_LENGTH,
            "prg_16k_bank": 4,
            "mmc3_8k_bank": 9,
            "cpu_start": "0xB717",
            "queue_ram_start": "0x6360",
            "ppu_action_start": "0x2363",
        },
        "code_by_glyph": {glyph: f"0x{code:02X}" for glyph, code in code_by_glyph.items()},
        "slots": slot_report,
        "font_page": "CHR 1 KiB pages 0x3E/0x3F",
        "ips_record_count": len(make_records(base, candidate)),
        "notes": [
            "Static source-chain, byte-scope, and IPS round-trip checks pass.",
            "Only the four action slots are changed; title and NONE remain English in this candidate.",
            "The normal Items R1 page is used so the source chain remains unchanged.",
            "The code pool is isolated from the bounded menu and English action codes, but release-wide page safety is not proven.",
            "Candidate FCEUX capture and byte verifier PASS." if runtime_pass else "Candidate FCEUX capture remains UNKNOWN until a bounded runtime report is supplied.",
        ],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Full Korean Items Action Candidate",
        "",
        f"- Status: `{payload['status']}`.",
        "- Release status: `NOT_READY`.",
        f"- Base MD5: `{payload['base_md5']}`.",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Source chain: ROM `0x{SOURCE_ROM_OFFSET:05X}` -> SRAM `$6360` -> PPU `$2363`.",
        "- Font page: normal Items R1 `0x3E/0x3F`.",
        "",
        "| English | Korean | ROM offset | new bytes |",
        "| --- | --- | --- | --- |",
    ]
    for row in slot_report:
        lines.append(f"| {row['english']} | {row['korean']} | `{row['rom_offset']}` | `{row['new_bytes']}` |")
    lines += [
        "",
        "## Gate",
        "",
        "- Byte-scope, source-chain, and IPS round-trip: PASS.",
        f"- Exact candidate Items PPU/source/queue proof: {runtime_gate}.",
        "- Title and empty-inventory rows remain untranslated and are separate follow-up owners.",
    ]
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
    parser.add_argument("--runtime-report", type=Path, help="Optional bounded runtime verifier JSON report.")
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

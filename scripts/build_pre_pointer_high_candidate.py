#!/usr/bin/env python3
"""Build a bounded Korean candidate for the fixed high-code item labels.

The English reference uses the 0x81-0x9A dialogue-code contract in the fixed
Bank 1 pre-pointer table.  This builder promotes only the ten rows already
classified as glyph-complete and control-free, then places the required Korean
8x16 tiles in the matching Bank 7 high-code slots.  It is a probe candidate:
the shared high-code page is not release-proven for every other screen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ines_layout, parse_ips
from build_patch import make_records, write_ips
from build_opening_dialogue_8x16_proof import default_tall_font
from korean_tile_font import render_tall_tiles
from rom_utils import REPO_ROOT


DEFAULT_INPUT = (
    REPO_ROOT
    / "output"
    / "full_korean_items_title_none_nonpointer_candidate"
    / "kunio_period_drama_korean_expanded_nonpointer_candidate.nes"
)
DEFAULT_BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
DEFAULT_INVENTORY = REPO_ROOT / "rom_analysis" / "pre_pointer_korean_candidates.json"
DEFAULT_REFERENCE_IPS = REPO_ROOT / "tools" / "reference" / "TSe-v10.ips"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_FONT = REPO_ROOT / "font" / "korean_font_8x16.bin"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_pre_pointer_high_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_pre_pointer_high_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_pre_pointer_high_candidate.md"
OUT_STEM = "kunio_period_drama_korean_pre_pointer_high_candidate"

TARGET_OFFSETS = {
    0x05AEB,
    0x05B1B,
    0x05B24,
    0x05B4E,
    0x05B61,
    0x05B69,
    0x05B85,
    0x05B8B,
    0x05BA2,
    0x05CE0,
}
HIGH_CODE_START = 0x81
HIGH_CODE_END = 0x9A
CHR_BANK7 = 7
CHR_TILE_SIZE = 16
BOTTOM_TILE_DELTA = 0x20


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def load_inventory(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = payload["rows"]
    selected = [
        row
        for row in rows
        if int(str(row["rom_offset"]), 16) in TARGET_OFFSETS
    ]
    if {int(str(row["rom_offset"]), 16) for row in selected} != TARGET_OFFSETS:
        raise ValueError("inventory does not contain the complete bounded target set")
    for row in selected:
        if row["readiness"] != "MAPPED_RUNTIME_UNKNOWN":
            raise ValueError(f"target is no longer safe: {row['record_id']} {row['readiness']}")
        if row["control_bytes"] or row["missing_glyphs"]:
            raise ValueError(f"target has a control or missing glyph: {row['record_id']}")
        if not row["korean_text"] or any(char.isspace() for char in str(row["korean_text"])):
            raise ValueError(f"target wording is not a compact glyph run: {row['record_id']}")
    return sorted(selected, key=lambda row: int(str(row["rom_offset"]), 16))


def load_glyphs(char_map_path: Path, font_path: Path) -> dict[str, bytes]:
    char_map = json.loads(char_map_path.read_text(encoding="utf-8"))
    characters = char_map["sorted"]
    font = font_path.read_bytes()
    if len(font) < len(characters) * 32:
        raise ValueError("Korean 8x16 font binary is incomplete")
    return {
        str(character): font[index * 32 : index * 32 + 32]
        for index, character in enumerate(characters)
    }


def tile_offset(layout, tile: int) -> int:
    start = layout.chr_start + CHR_BANK7 * layout.chr_bank_size
    offset = start + tile * CHR_TILE_SIZE
    if not start <= offset < offset + CHR_TILE_SIZE <= layout.chr_end:
        raise ValueError(f"Bank 7 tile escaped the ROM: 0x{tile:03X}")
    return offset


def encode_rows(rows: list[dict[str, object]], glyph_codes: dict[str, int], base: bytes, current: bytes, reference: bytes, input_candidate: bytes) -> tuple[bytearray, list[dict[str, object]]]:
    patched = bytearray(current)
    report: list[dict[str, object]] = []
    for row in rows:
        offset = int(str(row["rom_offset"]), 16)
        raw = bytes.fromhex(str(row["raw_bytes"]))
        payload_length = int(row["payload_length"])
        if input_candidate[offset : offset + len(raw)] != base[offset : offset + len(raw)]:
            raise ValueError(f"input candidate drift at 0x{offset:05X}")
        if raw != reference[offset : offset + len(raw)]:
            raise ValueError(f"English reference drift at 0x{offset:05X}")
        encoded_text = bytes(glyph_codes[char] for char in str(row["korean_text"]))
        if len(encoded_text) > payload_length:
            raise ValueError(f"Korean wording exceeds fixed width at 0x{offset:05X}")
        replacement = encoded_text + bytes([0xFF]) * (payload_length - len(encoded_text) + 1)
        if len(replacement) != len(raw):
            raise AssertionError("replacement length does not preserve the FF record")
        patched[offset : offset + len(replacement)] = replacement
        report.append(
            {
                "record_id": row["record_id"],
                "english": row["english_text"],
                "korean": row["korean_text"],
                "rom_offset": f"0x{offset:05X}",
                "old_bytes": raw.hex(" ").upper(),
                "new_bytes": replacement.hex(" ").upper(),
                "length": len(replacement),
            }
        )
    return patched, report


def build(
    input_rom: Path,
    base_rom: Path,
    inventory_path: Path,
    reference_ips: Path,
    char_map_path: Path,
    font_path: Path,
    output_dir: Path,
    report_json: Path,
    report_markdown: Path,
) -> dict[str, object]:
    base = base_rom.read_bytes()
    input_candidate = input_rom.read_bytes()
    if len(input_candidate) < len(base):
        raise ValueError("input candidate is shorter than the base ROM")
    rows = load_inventory(inventory_path)
    reference_records, reference_truncate = parse_ips(reference_ips.read_bytes())
    reference = apply_records(base, reference_records, reference_truncate)
    # Keep the English patch's executable/CHR structure, then reapply every
    # already-proven change from the current Korean composition on top.
    composed = bytearray(reference)
    for offset in range(len(base)):
        if input_candidate[offset] != base[offset]:
            composed[offset] = input_candidate[offset]
    if len(input_candidate) > len(base):
        composed.extend(input_candidate[len(base):])
    current = bytes(composed)
    glyph_order = tuple(dict.fromkeys("".join(str(row["korean_text"]) for row in rows)))
    char_map = json.loads(char_map_path.read_text(encoding="utf-8"))
    available_glyphs = set(char_map["sorted"])
    missing = sorted(set(glyph_order) - available_glyphs)
    if missing:
        raise ValueError(f"font asset is missing: {missing}")
    codes = {glyph: HIGH_CODE_START + index for index, glyph in enumerate(glyph_order)}
    if max(codes.values(), default=HIGH_CODE_START - 1) > HIGH_CODE_END:
        raise ValueError("bounded high-code pool overflowed 0x81-0x9A")

    layout = parse_ines_layout(base)
    patched, source_rows = encode_rows(rows, codes, base, current, reference, input_candidate)
    font_rows: list[dict[str, object]] = []
    for glyph, code in codes.items():
        top, bottom = render_tall_tiles(glyph, font_path=font_path, threshold=92)
        top_offset = tile_offset(layout, 0x100 + code)
        bottom_offset = tile_offset(layout, 0x100 + code + BOTTOM_TILE_DELTA)
        patched[top_offset : top_offset + CHR_TILE_SIZE] = top
        patched[bottom_offset : bottom_offset + CHR_TILE_SIZE] = bottom
        font_rows.append(
            {
                "glyph": glyph,
                "code": f"0x{code:02X}",
                "top_tile": f"0x{0x100 + code:03X}",
                "bottom_tile": f"0x{0x100 + code + BOTTOM_TILE_DELTA:03X}",
                "top_rom_offset": f"0x{top_offset:05X}",
                "bottom_rom_offset": f"0x{bottom_offset:05X}",
            }
        )

    candidate = bytes(patched)
    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"{OUT_STEM}.nes"
    ips_path = output_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(candidate)
    records = make_records(base, candidate)
    write_ips(ips_path, records)

    payload: dict[str, object] = {
        "status": "BUILT_PRE_POINTER_HIGH_STATIC_PASS_RUNTIME_UNKNOWN",
        "release_status": "NOT_READY",
        "input_rom": str(input_rom),
        "input_md5": md5(input_candidate),
        "composed_input_md5": md5(current),
        "base_md5": md5(base),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "candidate_md5": md5(candidate),
        "target_count": len(source_rows),
        "targets": source_rows,
        "glyph_codes": {glyph: f"0x{code:02X}" for glyph, code in codes.items()},
        "font_rows": font_rows,
        "ips_record_count": len(records),
        "renderer_contract": {
            "input_codes": "0x81-0x9A",
            "bank": 7,
            "top_tile_base": "0x181",
            "bottom_tile_delta": "0x20",
            "terminator": "0xFF",
        },
        "known_limits": [
            "Only ten control-free, glyph-complete inventory rows are changed.",
            "The shared Bank 7 high-code page is not release-proven for every other screen.",
            "Natural route and native pixel proof remain pending.",
        ],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Full Korean Pre-Pointer High-Code Candidate",
        "",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Fixed high-code source rows: `{payload['target_count']}`.",
        f"- Korean high-code glyphs: `{len(codes)}`; code range `0x{HIGH_CODE_START:02X}-0x{max(codes.values()):02X}`.",
        f"- IPS records: `{len(records)}`; static scope and IPS construction completed.",
        "- English owner contract: Bank 1 fixed records, 0x81-0x9A input codes, Bank 7 8x16 top/bottom tiles.",
        "- Runtime status: pending bounded route; release status: `NOT_READY`.",
        "",
        "| record | offset | English | Korean | new bytes |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {row['record_id']} | `{row['rom_offset']}` | {row['english']} | {row['korean']} | `{row['new_bytes']}` |"
        for row in source_rows
    )
    lines += [
        "",
        "## Limits",
        "",
        "- This is a probe candidate, not a release ROM.",
        "- The shared high-code Bank 7 page must be checked against every other promoted screen.",
        "- The ten selected rows are intentionally separate from control-bearing and missing-glyph rows.",
    ]
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-rom", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--reference-ips", type=Path, default=DEFAULT_REFERENCE_IPS)
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--font", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()
    font_path = args.font.resolve() if args.font else default_tall_font(None)
    payload = build(
        args.input_rom.resolve(),
        args.base_rom.resolve(),
        args.inventory.resolve(),
        args.reference_ips.resolve(),
        args.char_map.resolve(),
        font_path,
        args.out_dir.resolve(),
        args.report_json.resolve(),
        args.report_markdown.resolve(),
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

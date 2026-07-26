#!/usr/bin/env python3
"""Build one reference-guided Korean opening-dialogue proof candidate.

This is deliberately not a release patch. It proves the complete path for one
real dialogue record: Japanese source record -> Korean tile-code record ->
Bank 7 Korean glyph tiles -> IPS that applies cleanly to the verified base ROM.
The candidate keeps the original record length and pointer unchanged, so it
does not rely on blind gameplay or pointer relocation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ines_layout, parse_ips
from build_patch import make_records, write_ips
from korean_tile_font import find_korean_font, render_tile, write_preview
from rom_utils import REPO_ROOT


BASE_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
POINTER_INDEX = 182
POINTER_ROM_OFFSET = 0x05F40
RECORD_ROM_OFFSET = 0x071B6
RECORD_LENGTH = 0x25
ORIGINAL_RECORD = bytes.fromhex(
    "88 96 9F 8B BB 9A A4 88 8C 98 B2 86 82 CA F8 F9 00 "
    "1C AE 0F 83 85 A4 1C AE 06 00 93 B2 9D AE 95 AE 13 84 CA FF"
)
CHR_BANK = 7
SPRITE_PATTERN_TABLE_1_TILE_BASE = 0x100
TILE_SIZE = 0x10

# `0x8A` and `0x8B` have renderer-specific branches, so this first proof
# intentionally leaves them unused even though the English patch draws J/K.
KOREAN_GLYPH_CODES = {
    "쿠": 0x81,
    "니": 0x82,
    "마": 0x83,
    "사": 0x84,
    "어": 0x85,
    "서": 0x86,
    "움": 0x87,
    "직": 0x88,
    "여": 0x89,
    "분": 0x8C,
    "조": 0x8D,
    "두": 0x8E,
    "목": 0x8F,
    "이": 0x90,
    "큰": 0x91,
    "일": 0x92,
    "야": 0x93,
}

DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_proof.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_proof.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_korean_font_preview.png"
OUT_STEM = "kunio_period_drama_korean_opening_dialogue_proof"


def resolve_base_rom(candidate: str | None) -> Path:
    if candidate:
        path = Path(candidate).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(f"base ROM not found: {path}")
    roms = sorted((REPO_ROOT / "rom").glob("*.nes"))
    if roms:
        return roms[0]
    raise FileNotFoundError("base ROM not found")


def physical_tile_for_code(code: int) -> int:
    return SPRITE_PATTERN_TABLE_1_TILE_BASE + code


def proof_record() -> bytes:
    code = KOREAN_GLYPH_CODES
    data = bytes(
        [
            code["쿠"], code["니"], code["마"], code["사"],
            0xBB, 0x00,
            code["어"], code["서"], code["움"], code["직"], code["여"], 0xCA,
            0xF8,
            code["분"], code["조"], 0x00,
            code["두"], code["목"], code["이"], 0x00,
            code["큰"], code["일"], code["이"], code["야"], 0xCA,
        ]
    )
    if len(data) >= RECORD_LENGTH:
        raise ValueError("proof dialogue unexpectedly does not fit the source record")
    return data + bytes(RECORD_LENGTH - len(data) - 1) + b"\xff"


PROOF_RECORD = proof_record()


def changed_spans(original: bytes, patched: bytes) -> list[tuple[int, int]]:
    offsets = [index for index, (left, right) in enumerate(zip(original, patched)) if left != right]
    if not offsets:
        return []
    spans: list[tuple[int, int]] = []
    start = previous = offsets[0]
    for offset in offsets[1:]:
        if offset != previous + 1:
            spans.append((start, previous + 1))
            start = offset
        previous = offset
    spans.append((start, previous + 1))
    return spans


def target_tile_offset(layout, code: int) -> int:
    if not 0 <= CHR_BANK < (layout.chr_end - layout.chr_start) // layout.chr_bank_size:
        raise ValueError(f"CHR bank {CHR_BANK} is outside this ROM")
    physical_tile = physical_tile_for_code(code)
    if not 0 <= physical_tile < layout.chr_bank_size // TILE_SIZE:
        raise ValueError(f"physical tile 0x{physical_tile:03X} is outside one CHR bank")
    return layout.chr_start + CHR_BANK * layout.chr_bank_size + physical_tile * TILE_SIZE


def apply_opening_proof(base: bytes, glyph_tiles: dict[int, bytes]) -> tuple[bytes, list[dict[str, object]]]:
    if len(ORIGINAL_RECORD) != RECORD_LENGTH or len(PROOF_RECORD) != RECORD_LENGTH:
        raise AssertionError("proof record length invariant failed")
    if base[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] != ORIGINAL_RECORD:
        raise ValueError("opening source record does not match the verified base bytes")

    layout = parse_ines_layout(base)
    patched = bytearray(base)
    patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = PROOF_RECORD
    targets: list[dict[str, object]] = [
        {
            "kind": "dialogue_record",
            "rom_offset": RECORD_ROM_OFFSET,
            "length": RECORD_LENGTH,
            "pointer_rom_offset": POINTER_ROM_OFFSET,
        }
    ]
    for character, code in KOREAN_GLYPH_CODES.items():
        tile = glyph_tiles.get(code)
        if tile is None:
            raise ValueError(f"missing Korean glyph tile for code 0x{code:02X}")
        if len(tile) != TILE_SIZE:
            raise ValueError(f"glyph tile for code 0x{code:02X} must be {TILE_SIZE} bytes")
        offset = target_tile_offset(layout, code)
        patched[offset:offset + TILE_SIZE] = tile
        targets.append(
            {
                "kind": "font_tile",
                "character": character,
                "code": f"0x{code:02X}",
                "physical_tile": f"0x{physical_tile_for_code(code):03X}",
                "rom_offset": offset,
                "length": TILE_SIZE,
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
        raise AssertionError(f"proof patch changed {len(escaped)} byte(s) outside the allowed spans")
    return bytes(patched), targets


def validate_english_reference_slots(base: bytes, ips_path: Path) -> dict[str, object]:
    records, truncate_size = parse_ips(ips_path.read_bytes())
    reference = apply_records(base, records, truncate_size)
    layout = parse_ines_layout(base)
    slots = []
    for character, code in KOREAN_GLYPH_CODES.items():
        offset = target_tile_offset(layout, code)
        if base[offset:offset + TILE_SIZE] == reference[offset:offset + TILE_SIZE]:
            raise ValueError(
                f"English reference did not change physical tile for code 0x{code:02X}"
            )
        slots.append(
            {
                "character": character,
                "code": f"0x{code:02X}",
                "physical_tile": f"0x{physical_tile_for_code(code):03X}",
                "rom_offset": f"0x{offset:05X}",
            }
        )
    return {
        "ips_sha256": hashlib.sha256(ips_path.read_bytes()).hexdigest(),
        "validated_slots": slots,
    }


def build_glyph_tiles(
    font_path: str | Path | None,
    *,
    font_style: str = "raster",
) -> dict[int, bytes]:
    options: dict[str, object] = {"style": font_style}
    if font_style == "raster":
        options.update({"font_path": font_path, "target_pixels": 8, "threshold": 80})
    return {
        code: render_tile(character, **options)
        for character, code in KOREAN_GLYPH_CODES.items()
    }


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    lines = [
        "# Opening Dialogue Korean Proof Candidate",
        "",
        "Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED**",
        "",
        "This is a one-record proof build, not a release patch. It deliberately",
        "updates a real opening dialogue record at its original pointer and length.",
        "",
        "## Source",
        "",
        f"- Pointer index: `{source['pointer_index']}`",
        f"- Pointer ROM offset: `{source['pointer_rom_offset']}` (unchanged)",
        f"- Record ROM offset: `{source['record_rom_offset']}`",
        f"- Japanese source: {source['japanese_source']}",
        f"- English reference: {source['english_reference']}",
        f"- Korean proof: {source['korean_text']}",
        "",
        "## Safety Invariants",
        "",
        f"- Original and candidate record length: `{source['record_length']}` bytes.",
        "- No dialogue pointer table bytes change.",
        "- Font changes are restricted to Bank 7 physical tiles `0x181-0x191` with reserved `0x18A-0x18B` skipped.",
        f"- Changed-byte spans: `{candidate['changed_span_count']}`; escaped bytes: `{candidate['escaped_byte_count']}`.",
        "",
        "## Result",
        "",
        f"- Base MD5: `{candidate['base_md5']}`",
        f"- Candidate MD5: `{candidate['patched_md5']}`",
        f"- IPS: `{candidate['ips_path']}`",
        f"- ROM: `{candidate['rom_path']}`",
        "",
        "Visual verification is still required, but it must target the opening scene",
        "directly; this candidate must not be used as a reason to resume blind autoplay.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--reference-ips", required=True, help="English reference IPS")
    parser.add_argument("--font", help="Korean TrueType font path")
    parser.add_argument(
        "--font-style",
        choices=("raster", "handcrafted"),
        default="raster",
        help="Korean tile source; handcrafted is limited to the reviewed proof glyph set.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    args = parser.parse_args()

    rom_path = resolve_base_rom(args.rom)
    base = rom_path.read_bytes()
    actual_md5 = hashlib.md5(base).hexdigest()
    if actual_md5 != BASE_MD5:
        raise ValueError(f"unsupported base ROM MD5: {actual_md5}")
    ips_path = Path(args.reference_ips).expanduser()
    if not ips_path.is_file():
        raise FileNotFoundError(f"reference IPS not found: {ips_path}")

    reference = validate_english_reference_slots(base, ips_path)
    font = find_korean_font(args.font) if args.font_style == "raster" else None
    glyph_tiles = build_glyph_tiles(font, font_style=args.font_style)
    patched, targets = apply_opening_proof(base, glyph_tiles)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_output = args.out_dir / f"{OUT_STEM}.ips"
    rom_output = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_output, records)
    rom_output.write_bytes(patched)
    write_preview(
        list(KOREAN_GLYPH_CODES),
        args.preview,
        font_path=font,
        target_pixels=8,
        threshold=80,
        style=args.font_style,
    )

    changed = changed_spans(base, patched)
    payload = {
        "status": "CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED",
        "source": {
            "base_md5": BASE_MD5,
            "pointer_index": POINTER_INDEX,
            "pointer_rom_offset": f"0x{POINTER_ROM_OFFSET:05X}",
            "record_rom_offset": f"0x{RECORD_ROM_OFFSET:05X}",
            "record_length": RECORD_LENGTH,
            "original_record_bytes": ORIGINAL_RECORD.hex(" ").upper(),
            "candidate_record_bytes": PROOF_RECORD.hex(" ").upper(),
            "japanese_source": "くにまさ『はやくしねぇかい！ ぶんぞう親分がてぇへんなんでえ！』",
            "english_reference": "KUNIO: HURRY, SLUG! MR. BUNZO'S IN TROUBLE!",
            "korean_text": "쿠니마사: 어서 움직여! 분조 두목이 큰일이야!",
            "font": str(font),
            "font_style": args.font_style,
            "font_preview": str(args.preview),
        },
        "english_reference_validation": reference,
        "candidate": {
            "base_md5": actual_md5,
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": str(ips_output),
            "rom_path": str(rom_output),
            "ips_record_count": len(records),
            "changed_span_count": len(changed),
            "changed_spans": [
                {"start": f"0x{start:05X}", "end_exclusive": f"0x{end:05X}"}
                for start, end in changed
            ],
            "escaped_byte_count": 0,
            "targets": targets,
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report_markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"ips={ips_output}")
    print(f"rom={rom_output}")
    print(f"report_json={args.report_json}")
    print(f"report_markdown={args.report_markdown}")
    print(f"base_md5={actual_md5}")
    print(f"patched_md5={payload['candidate']['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a bounded Tatsuji name probe on top of the clean Korean candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from build_opening_dialogue_8x16_proof import default_tall_font
from korean_tile_font import render_tall_tiles
from rom_utils import REPO_ROOT
from analyze_reference_ips import parse_ines_layout


BASE_ROM = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
INPUT_ROM = REPO_ROOT / "output" / "full_korean_clean_merged_candidate" / "kunio_period_drama_korean_full_items_title_none_candidate.nes"
CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
FONT = default_tall_font(None)
OUT_DIR = REPO_ROOT / "output" / "tatsuji_clean_probe"
REPORT_JSON = REPO_ROOT / "rom_analysis" / "tatsuji_clean_probe.json"
REPORT_MD = REPO_ROOT / "rom_analysis" / "tatsuji_clean_probe.md"

TARGETS = (
    (0x048F4, bytes.fromhex("07 09 03")),
    (0x052A5, bytes.fromhex("82 84 7E")),
    (0x05BE5, bytes.fromhex("97 99 93")),
)
KOREAN_TEXT = "타츠지"
GLYPH_CODES = {"타": 0x89, "츠": 0x98, "지": 0xA1}
CHR_BANK = 7
CHR_TILE_SIZE = 16
BOTTOM_DELTA = 0x20


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def tile_offset(layout, code: int) -> tuple[int, int]:
    bank_start = layout.chr_start + CHR_BANK * layout.chr_bank_size
    top = bank_start + (0x100 + code) * CHR_TILE_SIZE
    bottom = bank_start + (0x100 + code + BOTTOM_DELTA) * CHR_TILE_SIZE
    return top, bottom


def build(input_rom: Path, base_rom: Path, out_dir: Path, report_json: Path, report_md: Path, font: Path) -> dict[str, object]:
    base = base_rom.read_bytes()
    source = input_rom.read_bytes()
    patched = bytearray(source)
    target_rows: list[dict[str, object]] = []
    encoded = bytes(GLYPH_CODES[char] for char in KOREAN_TEXT)

    for offset, expected in TARGETS:
        current = bytes(source[offset : offset + len(expected)])
        if current != expected:
            raise ValueError(f"target drift at 0x{offset:05X}: {current.hex(' ')} != {expected.hex(' ')}")
        patched[offset : offset + len(encoded)] = encoded
        target_rows.append(
            {
                "rom_offset": f"0x{offset:05X}",
                "old_bytes": expected.hex(" ").upper(),
                "new_bytes": encoded.hex(" ").upper(),
                "source": "Tatsuji",
                "korean": KOREAN_TEXT,
                "context": "boss/name label; visual route pending",
            }
        )

    layout = parse_ines_layout(base)
    font_rows: list[dict[str, object]] = []
    for glyph, code in GLYPH_CODES.items():
        top, bottom = render_tall_tiles(glyph, font_path=font, threshold=92)
        top_offset, bottom_offset = tile_offset(layout, code)
        patched[top_offset : top_offset + CHR_TILE_SIZE] = top
        patched[bottom_offset : bottom_offset + CHR_TILE_SIZE] = bottom
        font_rows.append(
            {
                "glyph": glyph,
                "code": f"0x{code:02X}",
                "top_rom_offset": f"0x{top_offset:05X}",
                "bottom_rom_offset": f"0x{bottom_offset:05X}",
            }
        )

    candidate = bytes(patched)
    out_dir.mkdir(parents=True, exist_ok=True)
    rom_path = out_dir / "kunio_period_drama_korean_tatsuji_probe.nes"
    ips_path = out_dir / "kunio_period_drama_korean_tatsuji_probe.ips"
    rom_path.write_bytes(candidate)
    records = make_records(base, candidate)
    write_ips(ips_path, records)

    payload: dict[str, object] = {
        "status": "BUILT_SINGLE_STRING_SOFT_GATE_PROBE",
        "release_status": "NOT_READY",
        "input_rom": str(input_rom),
        "input_md5": md5(source),
        "base_md5": md5(base),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "candidate_md5": md5(candidate),
        "string": KOREAN_TEXT,
        "targets": target_rows,
        "glyph_codes": {glyph: f"0x{code:02X}" for glyph, code in GLYPH_CODES.items()},
        "font_rows": font_rows,
        "ips_record_count": len(records),
        "runtime_status": "UNKNOWN_VISUAL_ROUTE_PENDING",
        "known_limits": [
            "The three offsets are equal-length candidate owners from the Tatsuji route queue.",
            "A visible boss/name screen has not yet been proven automatically.",
            "This probe must not be promoted into the release candidate without screen-context proof.",
        ],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Tatsuji Clean Probe",
        "",
        f"- Status: `{payload['status']}`.",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Test string: `{KOREAN_TEXT}`.",
        "- Release status: `NOT_READY`; visible boss/name screen proof is pending.",
        "",
        "## Owners",
        "",
        "| ROM offset | old bytes | new bytes | context |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(f"| `{row['rom_offset']}` | `{row['old_bytes']}` | `{row['new_bytes']}` | {row['context']} |" for row in target_rows)
    lines.extend(
        [
            "",
            "## Font Contract",
            "",
            "| glyph | code | top ROM offset | bottom ROM offset |",
            "| --- | --- | --- | --- |",
        ]
    )
    lines.extend(f"| {row['glyph']} | `{row['code']}` | `{row['top_rom_offset']}` | `{row['bottom_rom_offset']}` |" for row in font_rows)
    lines.extend(["", "The probe is an isolated soft-gate build. It is not a final Korean patch.", ""])
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text("\n".join(lines), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-rom", type=Path, default=INPUT_ROM)
    parser.add_argument("--base-rom", type=Path, default=BASE_ROM)
    parser.add_argument("--font", type=Path, default=FONT)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--report-json", type=Path, default=REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=REPORT_MD)
    args = parser.parse_args()
    payload = build(args.input_rom.resolve(), args.base_rom.resolve(), args.out_dir.resolve(), args.report_json.resolve(), args.report_markdown.resolve(), args.font.resolve())
    print(f"candidate={payload['candidate_rom']}")
    print(f"candidate_md5={payload['candidate_md5']}")
    print(f"targets={len(payload['targets'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

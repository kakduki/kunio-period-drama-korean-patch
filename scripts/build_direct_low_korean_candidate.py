#!/usr/bin/env python3
"""Compile the English patch's direct-low UI strings into a Korean candidate.

The English reference uses byte values 0x01-0x1A as 8x8 tile selectors for
labels in several PRG banks. This builder keeps that renderer contract,
assigns Korean glyphs to low-code CHR Bank 7 slots, and pads shorter Korean
labels with the existing blank code 0x00. It deliberately refuses missing
glyphs, overlong labels, and source-offset drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ips
from build_patch import CHR_BANK7_END, CHR_BANK7_START, CHR_TILE_SIZE, glyph_8x16_to_8x8_tile, make_records, write_ips
from rom_utils import REPO_ROOT


DEFAULT_INPUT = REPO_ROOT / "output" / "full_korean_candidate" / "kunio_period_drama_korean_full_candidate.nes"
DEFAULT_BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
DEFAULT_REFERENCE_IPS = REPO_ROOT / "tools" / "reference" / "TSe-v10.ips"
DEFAULT_REFERENCE_MAP = REPO_ROOT / "rom_analysis" / "english_patch_reference.json"
DEFAULT_LABELS = REPO_ROOT / "text_data" / "direct_low_korean_labels.json"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_direct_low_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_direct_low_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_direct_low_candidate.md"
OUT_STEM = "kunio_period_drama_korean_full_direct_low_candidate"
MAX_LOW_CODE = 0x7F


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def load_glyphs(char_map_path: Path, font_bin_path: Path) -> dict[str, bytes]:
    characters = json.loads(char_map_path.read_text(encoding="utf-8"))["sorted"]
    font_data = font_bin_path.read_bytes()
    expected = len(characters) * 32
    if len(font_data) < expected:
        raise ValueError(f"font binary is short: {len(font_data)} < {expected}")
    return {
        str(character): font_data[index * 32:index * 32 + 32]
        for index, character in enumerate(characters)
    }


def build(
    input_rom: Path,
    base_rom: Path,
    reference_ips: Path,
    reference_map: Path,
    labels_path: Path,
    char_map_path: Path,
    font_bin_path: Path,
    output_dir: Path,
    report_json: Path,
    report_markdown: Path,
    reserved_low_codes: set[int] | None = None,
) -> dict[str, object]:
    current = input_rom.read_bytes()
    base = base_rom.read_bytes()
    if len(current) < len(base):
        raise ValueError("input candidate is shorter than the verified base ROM")
    records, truncate_size = parse_ips(reference_ips.read_bytes())
    reference = apply_records(base, records, truncate_size)
    reference_data = json.loads(reference_map.read_text(encoding="utf-8"))
    labels = json.loads(labels_path.read_text(encoding="utf-8-sig"))
    glyphs = load_glyphs(char_map_path, font_bin_path)

    rows = list(reference_data["english_tile_alpha_runs"])
    if not rows:
        raise ValueError("reference map contains no direct-low text runs")

    translations: dict[str, str] = {}
    missing_labels: list[str] = []
    for row in rows:
        source = str(row["text"])
        translated = labels.get(source)
        if translated is None:
            missing_labels.append(source)
            continue
        translations[source] = str(translated)
    if missing_labels:
        raise ValueError(f"missing Korean labels: {sorted(set(missing_labels))}")

    ordered_glyphs: list[str] = []
    for source in translations:
        for character in translations[source]:
            if character not in ordered_glyphs:
                ordered_glyphs.append(character)
    missing_glyphs = sorted({character for character in ordered_glyphs if character not in glyphs})
    if missing_glyphs:
        raise ValueError(f"glyphs missing from font assets: {missing_glyphs}")
    reserved = set(reserved_low_codes or ())
    if any(code <= 0 or code > MAX_LOW_CODE for code in reserved):
        raise ValueError(f"reserved direct-low codes must be in 0x01-0x{MAX_LOW_CODE:02X}")
    available_codes = [code for code in range(1, MAX_LOW_CODE + 1) if code not in reserved]
    if len(ordered_glyphs) > len(available_codes):
        raise ValueError(
            f"direct-low glyph pool needs {len(ordered_glyphs)} codes; "
            f"available after reservation: {len(available_codes)}"
        )
    code_by_glyph = {
        character: available_codes[index] for index, character in enumerate(ordered_glyphs)
    }

    patched = bytearray(current)
    rows_report: list[dict[str, object]] = []
    for row in rows:
        source = str(row["text"])
        translated = translations[source]
        offset = int(row["rom_offset"])
        length = int(row["length"])
        base_bytes = base[offset:offset + length]
        reference_bytes = reference[offset:offset + length]
        current_bytes = current[offset:offset + length]
        if len(base_bytes) != length or len(reference_bytes) != length:
            raise ValueError(f"short direct-low source at 0x{offset:05X}")
        if current_bytes != base_bytes:
            raise ValueError(
                f"input candidate drift at 0x{offset:05X}: "
                f"{current_bytes.hex(' ').upper()} != base {base_bytes.hex(' ').upper()}"
            )
        leading_blanks = len(reference_bytes) - len(reference_bytes.lstrip(b"\x00"))
        visible_reference = reference_bytes[leading_blanks:]
        if len(translated) > length - leading_blanks:
            raise ValueError(f"translation {source!r}->{translated!r} exceeds visible width {length - leading_blanks}")
        if any(value == 0 or value > 0x1A for value in visible_reference):
            raise ValueError(f"reference run {source!r} is not direct-low ASCII bytes")
        encoded = b"\x00" * leading_blanks
        encoded += bytes(code_by_glyph[character] for character in translated)
        encoded += b"\x00" * (length - len(encoded))
        patched[offset:offset + length] = encoded
        rows_report.append(
            {
                "source": source,
                "translation": translated,
                "rom_offset": f"0x{offset:05X}",
                "length": length,
                "reference_bytes": reference_bytes.hex(" ").upper(),
                "new_bytes": encoded.hex(" ").upper(),
                "prg_bank": row["prg_bank"],
            }
        )

    for character, code in code_by_glyph.items():
        tile = 0x100 + code
        offset = CHR_BANK7_START + tile * CHR_TILE_SIZE
        if not CHR_BANK7_START <= offset < offset + CHR_TILE_SIZE <= CHR_BANK7_END:
            raise ValueError(f"glyph tile 0x{tile:03X} escaped CHR Bank 7")
        patched[offset:offset + CHR_TILE_SIZE] = glyph_8x16_to_8x8_tile(glyphs[character])

    candidate = bytes(patched)
    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"{OUT_STEM}.nes"
    ips_path = output_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(candidate)
    records_out = make_records(base, candidate)
    write_ips(ips_path, records_out)

    payload: dict[str, object] = {
        "status": "BUILT_RUNTIME_VISUAL_PENDING",
        "input_rom": str(input_rom),
        "input_md5": md5(current),
        "base_rom": str(base_rom),
        "base_md5": md5(base),
        "reference_ips": str(reference_ips),
        "reference_md5": md5(reference),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "candidate_md5": md5(candidate),
        "direct_low_run_count": len(rows_report),
        "direct_low_glyph_count": len(code_by_glyph),
        "reserved_low_codes": [f"0x{code:02X}" for code in sorted(reserved)],
        "ips_record_count": len(records_out),
        "glyph_codes": {character: f"0x{code:02X}" for character, code in code_by_glyph.items()},
        "rows": rows_report,
        "release_status": "NOT_READY",
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Full Direct-Low Korean Candidate",
        "",
        "This candidate preserves the English patch's direct-low 8x8 renderer contract and replaces every extracted direct-low label with a bounded Korean label.",
        "",
        f"- Input candidate MD5: `{payload['input_md5']}`.",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Direct-low runs: `{payload['direct_low_run_count']}`.",
        f'- Korean glyphs allocated: `{payload["direct_low_glyph_count"]}`; reserved low codes: `{", ".join(payload["reserved_low_codes"]) or "none"}`.',
        f"- IPS records: `{payload['ips_record_count']}`; IPS round trip is checked by the builder.",
        "- Runtime/screen status: pending bounded per-context proof.",
        "- Release status: `NOT_READY`.",
        "",
        "## Sample Rows",
        "",
        "| bank | ROM offset | English | Korean | new bytes |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows_report[:40]:
        lines.append(
            f"| {row['prg_bank']} | `{row['rom_offset']}` | {row['source']} | {row['translation']} | `{row['new_bytes']}` |"
        )
    lines += [
        "",
        "## Gate",
        "",
        "- Build and byte-scope proof: PASS if the JSON report exists and IPS round trip succeeds.",
        "- Exact screen proof: UNKNOWN until each shared Bank 7 context is captured.",
        "- This candidate does not replace the relocated pointer-dialogue records; it composes with the current full pointer/menu candidate.",
    ]
    report_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-rom", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--reference-ips", type=Path, default=DEFAULT_REFERENCE_IPS)
    parser.add_argument("--reference-map", type=Path, default=DEFAULT_REFERENCE_MAP)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--font-bin", type=Path, default=DEFAULT_FONT_BIN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()
    payload = build(
        args.input_rom.resolve(),
        args.base_rom.resolve(),
        args.reference_ips.resolve(),
        args.reference_map.resolve(),
        args.labels.resolve(),
        args.char_map.resolve(),
        args.font_bin.resolve(),
        args.out_dir.resolve(),
        args.report_json.resolve(),
        args.report_markdown.resolve(),
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a bounded expansion over the composed Korean candidate.

This builder owns only control-free, FF-terminated pre-pointer labels.  It
preserves the already-composed candidate and its existing 0x81-0x9A glyph
contract, then allocates a soft-gate extension in 0x9B-0xB5.  Rows that need a
control skeleton, exceed their fixed width, lack a font glyph, or overflow the
new pool remain untouched and are reported explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ips, parse_ines_layout
from build_patch import make_records, write_ips
from build_opening_dialogue_8x16_proof import default_tall_font
from korean_tile_font import render_tall_tiles
from rom_utils import REPO_ROOT


DEFAULT_INPUT = REPO_ROOT / "output" / "full_korean_expanded_candidate" / "kunio_period_drama_korean_expanded_candidate.nes"
DEFAULT_BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
DEFAULT_LABELS = REPO_ROOT / "text_data" / "pre_pointer_korean_labels.json"
DEFAULT_EXISTING_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_expanded_candidate.json"
DEFAULT_REFERENCE_IPS = REPO_ROOT / "tools" / "reference" / "TSe-v10.ips"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "pre_pointer_full_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "pre_pointer_full_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pre_pointer_full_candidate.md"
OUT_STEM = "kunio_period_drama_korean_pre_pointer_full_candidate"

CODE_START = 0x9B
CODE_END = 0xB5
CHR_BANK7 = 7
CHR_TILE_SIZE = 16
BOTTOM_TILE_DELTA = 0x20
PROTECTED_RANGES = ((0x0561B, 0x0561B + 5),)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def interval_overlaps(start: int, length: int, ranges: tuple[tuple[int, int], ...]) -> bool:
    end = start + length
    return any(start < protected_end and end > protected_start for protected_start, protected_end in ranges)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_glyphs(char_map_path: Path, font_path: Path) -> dict[str, bytes]:
    char_map = load_json(char_map_path)
    characters = [str(value) for value in char_map["sorted"]]
    font = font_path.read_bytes()
    if len(font) < len(characters) * 32:
        raise ValueError("Korean 8x16 font binary is incomplete")
    return {character: font[index * 32 : index * 32 + 32] for index, character in enumerate(characters)}


def tile_offset(layout, tile: int) -> int:
    start = layout.chr_start + CHR_BANK7 * layout.chr_bank_size
    offset = start + tile * CHR_TILE_SIZE
    if not start <= offset < offset + CHR_TILE_SIZE <= layout.chr_end:
        raise ValueError(f"Bank 7 tile escaped the ROM: 0x{tile:03X}")
    return offset


def row_priority(row: dict[str, object]) -> tuple[int, int]:
    source = str(row.get("source", ""))
    source_rank = {"curated_alias": 0, "direct_low_label": 1, "translation_glossary_note": 2, "romaji_fallback": 3}.get(source, 9)
    return source_rank, int(str(row["rom_offset"]), 16)


def build(
    input_rom: Path,
    base_rom: Path,
    labels_path: Path,
    existing_report_path: Path,
    reference_ips: Path,
    char_map_path: Path,
    font_path: Path,
    output_dir: Path,
    report_json: Path,
    report_markdown: Path,
    runtime_report: Path | None = None,
    out_stem: str = OUT_STEM,
) -> dict[str, object]:
    base = base_rom.read_bytes()
    input_candidate = input_rom.read_bytes()
    if len(input_candidate) < len(base):
        raise ValueError("input candidate is shorter than the base ROM")
    labels = load_json(labels_path)
    existing = load_json(existing_report_path)
    reference_records, reference_truncate = parse_ips(reference_ips.read_bytes())
    reference = apply_records(base, reference_records, reference_truncate)
    char_glyphs = load_glyphs(char_map_path, font_path)
    runtime_gate = load_json(runtime_report) if runtime_report else None
    approved_ids = {str(value) for value in (runtime_gate or {}).get("approved_ids", [])}
    existing_codes = {str(glyph): int(str(code), 16) for glyph, code in dict(existing.get("glyph_codes", {})).items()}
    existing_offsets = {int(str(row["rom_offset"]), 16) for row in existing.get("targets", [])}
    glyph_codes = dict(existing_codes)
    new_glyphs: list[str] = []
    patched = bytearray(input_candidate)
    rows_report: list[dict[str, object]] = []
    patched_count = 0
    status_counts: dict[str, int] = {}

    candidate_rows = (row for row in labels.get("records", []) if row.get("patch_ready"))
    if runtime_report:
        candidate_rows = (row for row in candidate_rows if str(row.get("record_id")) in approved_ids)
    candidates = sorted(candidate_rows, key=row_priority)
    for row in candidates:
        offset = int(str(row["rom_offset"]), 16)
        raw = bytes.fromhex(str(row["raw_bytes"]))
        width = len(raw) - 1 if raw.endswith(b"\xFF") else -1
        status = "PATCHED"
        reason = ""
        if offset in existing_offsets:
            status, reason = "PRESERVED_EXISTING", "already-owned-composed-row"
        elif width < 0:
            status, reason = "SKIPPED_UNTERMINATED", "missing-ff-terminator"
        elif interval_overlaps(offset, len(raw), PROTECTED_RANGES):
            status, reason = "SKIPPED_PROTECTED_OVERLAP", "protected-item-name-source"
        elif list(row.get("control_bytes", [])):
            status, reason = "SKIPPED_CONTROL", "control-skeleton-required"
        elif input_candidate[offset : offset + len(raw)] not in (base[offset : offset + len(raw)], reference[offset : offset + len(raw)]):
            status, reason = "SKIPPED_INPUT_DRIFT", "input-candidate-does-not-own-japanese-or-english-template"
        elif len(str(row["korean_text"])) > width:
            status, reason = "SKIPPED_WIDTH", f"{len(str(row['korean_text']))}>{width}"
        elif not set(str(row["korean_text"])) <= set(char_glyphs):
            status, reason = "SKIPPED_MISSING_GLYPH", "font-char-map-missing"
        else:
            missing = [char for char in dict.fromkeys(str(row["korean_text"])) if char not in glyph_codes]
            if len(new_glyphs) + len(missing) > CODE_END - CODE_START + 1:
                status, reason = "SKIPPED_GLYPH_OVERFLOW", "soft-gate-0x9B-0xB5-pool"
            else:
                for char in missing:
                    glyph_codes[char] = CODE_START + len(new_glyphs)
                    new_glyphs.append(char)
                encoded = bytes(glyph_codes[char] for char in str(row["korean_text"]))
                replacement = encoded + bytes([0xFF]) * (width - len(encoded) + 1)
                patched[offset : offset + len(replacement)] = replacement
                patched_count += 1
        status_counts[status] = status_counts.get(status, 0) + 1
        rows_report.append({
            "record_id": row["record_id"],
            "rom_offset": f"0x{offset:05X}",
            "english": row["english_text"],
            "korean": row["korean_text"],
            "source": row["source"],
            "confidence": row["confidence"],
            "status": status,
            "reason": reason,
            "width": width,
        })

    layout = parse_ines_layout(base)
    font_rows: list[dict[str, object]] = []
    for glyph in new_glyphs:
        code = glyph_codes[glyph]
        top, bottom = render_tall_tiles(glyph, font_path=font_path, threshold=92)
        top_offset = tile_offset(layout, 0x100 + code)
        bottom_offset = tile_offset(layout, 0x100 + code + BOTTOM_TILE_DELTA)
        patched[top_offset : top_offset + CHR_TILE_SIZE] = top
        patched[bottom_offset : bottom_offset + CHR_TILE_SIZE] = bottom
        font_rows.append({
            "glyph": glyph,
            "code": f"0x{code:02X}",
            "top_tile": f"0x{0x100 + code:03X}",
            "bottom_tile": f"0x{0x100 + code + BOTTOM_TILE_DELTA:03X}",
            "top_rom_offset": f"0x{top_offset:05X}",
            "bottom_rom_offset": f"0x{bottom_offset:05X}",
        })

    candidate = bytes(patched)
    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"{out_stem}.nes"
    ips_path = output_dir / f"{out_stem}.ips"
    rom_path.write_bytes(candidate)
    records = make_records(base, candidate)
    write_ips(ips_path, records)
    payload: dict[str, object] = {
        "status": "BUILT_PRE_POINTER_EXPANDED_SOFT_GATE",
        "release_status": "NOT_READY",
        "input_rom": str(input_rom),
        "input_md5": md5(input_candidate),
        "base_md5": md5(base),
        "reference_md5": md5(reference),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "candidate_md5": md5(candidate),
        "label_record_count": len(candidates),
        "patched_count": patched_count,
        "runtime_gate": str(runtime_report) if runtime_report else None,
        "runtime_approved_count": len(approved_ids) if runtime_report else None,
        "status_counts": status_counts,
        "rows": rows_report,
        "glyph_codes": {glyph: f"0x{code:02X}" for glyph, code in glyph_codes.items()},
        "new_glyphs": new_glyphs,
        "font_rows": font_rows,
        "ips_record_count": len(records),
        "renderer_contract": {
            "existing_input_codes": "0x81-0x9A",
            "soft_extension_codes": "0x9B-0xB5",
            "bank": 7,
            "top_tile_base": "0x181",
            "bottom_tile_delta": "0x20",
            "terminator": "0xFF",
        },
        "known_limits": [
            "Only control-free FF-delimited pre-pointer rows are considered.",
            "0x9B-0xB5 is a soft-gate renderer extension and is not native-pixel proven.",
            "Fallback name transliterations require semantic review.",
            "Natural route and release visual proof remain pending.",
        ],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Pre-Pointer Full Candidate",
        "",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Patch-ready records considered: `{payload['label_record_count']}`.",
        f"- Newly patched records: `{payload['patched_count']}`.",
        f"- Runtime gate: `{payload['runtime_gate'] or 'not applied'}`.",
        f"- New soft-gate glyphs: `{len(new_glyphs)}` in `0x9B-0xB5`.",
        f"- Status counts: `{json.dumps(status_counts, ensure_ascii=False)}`.",
        "- Release status: `NOT_READY`; this candidate is for bounded runtime validation.",
        "",
        "| record | offset | English | Korean | status | reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {row['record_id']} | `{row['rom_offset']}` | {row['english']} | {row['korean']} | {row['status']} | {row['reason']} |"
        for row in rows_report
    )
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-rom", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--existing-report", type=Path, default=DEFAULT_EXISTING_REPORT)
    parser.add_argument("--reference-ips", type=Path, default=DEFAULT_REFERENCE_IPS)
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--font", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--runtime-report", type=Path, default=None)
    parser.add_argument("--out-stem", default=OUT_STEM)
    args = parser.parse_args()
    font_path = args.font.resolve() if args.font else default_tall_font(None)
    payload = build(
        args.input_rom.resolve(), args.base_rom.resolve(), args.labels.resolve(), args.existing_report.resolve(),
        args.reference_ips.resolve(), args.char_map.resolve(), font_path,
        args.out_dir.resolve(), args.report_json.resolve(), args.report_markdown.resolve(),
        args.runtime_report.resolve() if args.runtime_report else None, args.out_stem,
    )
    print(json.dumps({
        "status": payload["status"], "candidate_md5": payload["candidate_md5"],
        "patched_count": payload["patched_count"], "status_counts": payload["status_counts"],
        "new_glyph_count": len(payload["new_glyphs"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

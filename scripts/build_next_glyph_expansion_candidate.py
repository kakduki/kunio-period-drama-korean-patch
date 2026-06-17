#!/usr/bin/env python3
"""Build a local font-expansion ROM/IPS from the next glyph expansion plan.

This writes CHR glyphs only. It does not promote or rewrite additional PRG text.
The generated ROM/IPS stays under output/ for local testing; the tracked evidence
is the report in rom_analysis/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import (
    CHR_BANK7_END,
    CHR_BANK7_START,
    CHR_TILE_SIZE,
    glyph_8x16_to_8x8_tile,
    make_records,
    write_ips,
)
from rom_utils import REPO_ROOT, find_rom_path


SLOT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
EXPANSION_PLAN = REPO_ROOT / "rom_analysis" / "next_glyph_expansion_plan.json"
FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
BASE_FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_plan_v0.2.nes"
OUT_DIR = REPO_ROOT / "output"
REPORT_DIR = REPO_ROOT / "rom_analysis"
OUT_STEM = "kunio_period_drama_korean_font_expansion_v0.5_batch"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def load_slots(batch_size: int) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
    base_plan = json.loads(SLOT_PLAN.read_text(encoding="utf-8"))
    expansion = json.loads(EXPANSION_PLAN.read_text(encoding="utf-8"))
    slots = list(base_plan["slots"])
    slots.extend(expansion["next_slots"][:batch_size])
    return slots, base_plan, expansion


def load_font_glyphs() -> dict[str, bytes]:
    characters = json.loads(CHAR_MAP.read_text(encoding="utf-8"))["sorted"]
    font_data = FONT_BIN.read_bytes()
    expected_size = len(characters) * 32
    if len(font_data) < expected_size:
        raise RuntimeError(
            f"Font binary is too small for char_map: {len(font_data)} < {expected_size}"
        )
    return {
        str(ch): font_data[index * 32:index * 32 + 32]
        for index, ch in enumerate(characters)
    }


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def write_markdown(report_path: Path, report: dict[str, object]) -> None:
    lines = [
        "# Font Expansion Candidate Report",
        "",
        f"- Candidate: **{report['candidate']}**",
        f"- Base ROM MD5: `{report['base_md5']}`",
        f"- Patched ROM MD5: `{report['patched_md5']}`",
        f"- Glyphs written: **{report['glyphs_written']}**",
        f"- Added glyphs: **{report['added_glyph_count']}**",
        f"- Changed bytes: **{report['changed_bytes']}**",
        f"- Added glyph changed bytes: **{report['added_glyph_changed_bytes']}**",
        f"- IPS records: **{report['ips_records']}**",
        f"- Escaped CHR Bank 07 bytes: **{report['escaped_chr_bank7_bytes']}**",
        f"- Local ROM: `{report['patched_rom_path']}`",
        f"- Local IPS: `{report['ips_path']}`",
        "",
        "## Added Glyphs",
        "",
        "| glyph | tile | PRG byte (+0x7A) | rows needing it |",
        "| --- | --- | --- | ---: |",
    ]
    for row in report["added_slots"]:
        lines.append(
            f"| {row['glyph']} | `{row['tile']}` | `{row['prg_plus_0x7a_byte']}` | "
            f"{row.get('rows_needing_it', '')} |"
        )

    lines += [
        "",
        "## Rule",
        "",
        "- This candidate expands font coverage only; it is not a new text patch release.",
        "- Additional PRG text promotion still requires ROM byte evidence, screen evidence, and length/padding safety.",
        "- Generated `.nes` files are local test artifacts and must not be distributed.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(batch_size: int) -> dict[str, object]:
    rom_path = find_rom_path(None).resolve()
    original = rom_path.read_bytes()
    if not BASE_FONT_ROM.exists():
        raise FileNotFoundError(f"Base font ROM not found: {BASE_FONT_ROM}")
    base_font = BASE_FONT_ROM.read_bytes()
    if len(base_font) != len(original):
        raise RuntimeError(
            f"Base font ROM size differs from base ROM: {len(base_font)} != {len(original)}"
        )
    patched = bytearray(base_font)
    font_glyphs = load_font_glyphs()
    slots, base_plan, expansion = load_slots(batch_size)
    base_count = len(base_plan["slots"])
    added_slots = slots[base_count:]

    changed_offsets: list[int] = []
    slot_reports: list[dict[str, object]] = []
    for slot in added_slots:
        glyph = str(slot["glyph"])
        tile = int(str(slot["tile"]), 16)
        target_offset = CHR_BANK7_START + tile * CHR_TILE_SIZE
        target_end = target_offset + CHR_TILE_SIZE
        if not CHR_BANK7_START <= target_offset < target_end <= CHR_BANK7_END:
            raise RuntimeError(f"Tile 0x{tile:03X} escaped CHR Bank 07")
        if glyph not in font_glyphs:
            raise RuntimeError(f"Glyph {glyph!r} is missing from {rel(CHAR_MAP)}")

        tile_data = glyph_8x16_to_8x8_tile(font_glyphs[glyph])
        old = bytes(patched[target_offset:target_end])
        patched[target_offset:target_end] = tile_data
        changed_offsets.extend(
            offset
            for offset, (old_byte, new_byte) in enumerate(zip(old, tile_data), start=target_offset)
            if old_byte != new_byte
        )
        slot_reports.append(
            {
                "glyph": glyph,
                "tile": slot["tile"],
                "rom_offset": f"0x{target_offset:05X}",
                "prg_plus_0x7a_byte": slot["prg_plus_0x7a_byte"],
                "rows_needing_it": slot.get("rows_needing_it"),
                "is_added_glyph": True,
            }
        )

    all_changed_offsets = [
        offset
        for offset, (old_byte, new_byte) in enumerate(zip(original, patched))
        if old_byte != new_byte
    ]
    escaped = [offset for offset in all_changed_offsets if not CHR_BANK7_START <= offset < CHR_BANK7_END]
    if escaped:
        raise RuntimeError(f"{len(escaped)} changed byte(s) escaped CHR Bank 07")

    records = make_records(original, bytes(patched))
    stem = f"{OUT_STEM}{batch_size:02d}"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ips_path = OUT_DIR / f"{stem}.ips"
    patched_path = OUT_DIR / f"{stem}.nes"
    report_json = REPORT_DIR / f"{stem}_report.json"
    report_md = REPORT_DIR / f"{stem}_report.md"

    write_ips(ips_path, records)
    patched_path.write_bytes(patched)

    report = {
        "candidate": f"v0.5 font-expansion batch {batch_size}",
        "source_slot_plan": rel(SLOT_PLAN),
        "source_expansion_plan": rel(EXPANSION_PLAN),
        "source_font_bin": rel(FONT_BIN),
        "source_char_map": rel(CHAR_MAP),
        "source_base_font_rom": rel(BASE_FONT_ROM),
        "base_rom": rel(rom_path),
        "base_md5": md5(original),
        "base_font_rom_md5": md5(base_font),
        "patched_md5": md5(bytes(patched)),
        "patched_rom_path": rel(patched_path),
        "ips_path": rel(ips_path),
        "report_md": rel(report_md),
        "chr_bank7_range": [f"0x{CHR_BANK7_START:05X}", f"0x{CHR_BANK7_END - 1:05X}"],
        "glyphs_written": len(slots),
        "base_glyph_count": base_count,
        "added_glyph_count": len(added_slots),
        "changed_bytes": len(all_changed_offsets),
        "added_glyph_changed_bytes": len(changed_offsets),
        "escaped_chr_bank7_bytes": len(escaped),
        "ips_records": len(records),
        "coverage_simulation": next(
            (
                row
                for row in expansion["batch_simulations"]
                if int(row["requested_extra_glyphs"]) == batch_size
            ),
            None,
        ),
        "added_slots": slot_reports,
        "all_slots": slot_reports,
    }
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report_md, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    report = build(args.batch_size)
    print(f"patched ROM: {report['patched_rom_path']}")
    print(f"IPS: {report['ips_path']}")
    print(f"report: {report['report_md']}")
    print(
        f"glyphs={report['glyphs_written']} added={report['added_glyph_count']} "
        f"changed_bytes={report['changed_bytes']} ips_records={report['ips_records']}"
    )
    print(f"patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

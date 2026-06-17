#!/usr/bin/env python3
"""Validate the compact Korean CHR Bank 07 slot plan and patched ROM outputs."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from build_patch import CHR_BANK7_END, CHR_BANK7_START, CHR_TILE_SIZE
from rom_utils import REPO_ROOT, find_rom_path


ROOT = REPO_ROOT
PLAN_JSON = ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
V02_REPORT = ROOT / "output" / "kunio_period_drama_korean_plan_v0.2_build_report.json"
V02_ROM = ROOT / "output" / "kunio_period_drama_korean_plan_v0.2.nes"
V04_REPORT = ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4_equal_length_static_build_report.json"
V04_ROM = ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes"
OUT_MD = ROOT / "rom_analysis" / "chr_bank07_plan_status.md"
OUT_JSON = ROOT / "rom_analysis" / "chr_bank07_plan_status.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_hex(value: str) -> int:
    return int(value, 16)


def fmt(value: int) -> str:
    return f"0x{value:05X}"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def diff_offsets(original: bytes, patched: bytes) -> list[int]:
    if len(original) != len(patched):
        raise ValueError("ROM sizes differ")
    return [idx for idx, (a, b) in enumerate(zip(original, patched)) if a != b]


def summarize_diff(offsets: list[int]) -> dict[str, object]:
    chr_bank7 = [offset for offset in offsets if CHR_BANK7_START <= offset < CHR_BANK7_END]
    prg_or_header = [offset for offset in offsets if offset < CHR_BANK7_START]
    after_bank7 = [offset for offset in offsets if offset >= CHR_BANK7_END]
    return {
        "changed_bytes": len(offsets),
        "changed_range": [fmt(min(offsets)), fmt(max(offsets))] if offsets else None,
        "chr_bank7_changed_bytes": len(chr_bank7),
        "chr_bank7_changed_range": [fmt(min(chr_bank7)), fmt(max(chr_bank7))] if chr_bank7 else None,
        "pre_chr_bank7_changed_bytes": len(prg_or_header),
        "post_chr_bank7_changed_bytes": len(after_bank7),
        "escaped_chr_bank7_font_bytes": len(after_bank7),
    }


def contiguous_ranges(offsets: list[int]) -> list[tuple[int, int]]:
    if not offsets:
        return []
    ranges: list[tuple[int, int]] = []
    start = prev = offsets[0]
    for offset in offsets[1:]:
        if offset == prev + 1:
            prev = offset
            continue
        ranges.append((start, prev))
        start = prev = offset
    ranges.append((start, prev))
    return ranges


def main() -> int:
    plan = load_json(PLAN_JSON)
    v02_report = load_json(V02_REPORT)
    v04_report = load_json(V04_REPORT)
    original = Path(find_rom_path()).read_bytes()
    v02 = V02_ROM.read_bytes()
    v04 = V04_ROM.read_bytes()

    v02_offsets = diff_offsets(original, v02)
    v04_offsets = diff_offsets(original, v04)
    v02_summary = summarize_diff(v02_offsets)
    v04_summary = summarize_diff(v04_offsets)

    slots = plan["slots"]
    slot_offsets = [parse_hex(slot["rom_offset"]) for slot in slots]
    slot_tiles = [parse_hex(slot["tile"]) for slot in slots]
    prg_bytes = [slot["prg_plus_0x7a_byte"] for slot in slots]
    glyph_use_counts = Counter(
        label
        for slot in slots
        for label in slot.get("used_by_labels", [])
    )
    duplicate_prg_bytes = {
        byte: count
        for byte, count in Counter(prg_bytes).items()
        if count > 1
    }

    patch_tile_start, patch_tile_end = (parse_hex(value) for value in plan["patch_tile_range"])
    patch_slot_start = CHR_BANK7_START + patch_tile_start * CHR_TILE_SIZE
    patch_slot_end = CHR_BANK7_START + (patch_tile_end + 1) * CHR_TILE_SIZE - 1

    v04_prg_ranges = [
        (start, end)
        for start, end in contiguous_ranges([offset for offset in v04_offsets if offset < CHR_BANK7_START])
    ]
    v04_chr_ranges = [
        (start, end)
        for start, end in contiguous_ranges([offset for offset in v04_offsets if CHR_BANK7_START <= offset < CHR_BANK7_END])
    ]

    payload = {
        "source": {
            "plan": rel(PLAN_JSON),
            "v02_report": rel(V02_REPORT),
            "v02_rom": rel(V02_ROM),
            "v04_report": rel(V04_REPORT),
            "v04_rom": rel(V04_ROM),
        },
        "chr_bank7_range": [fmt(CHR_BANK7_START), fmt(CHR_BANK7_END - 1)],
        "patch_tile_range": plan["patch_tile_range"],
        "patch_slot_rom_range": [fmt(patch_slot_start), fmt(patch_slot_end)],
        "summary": {
            "available_slots": plan["available_slots"],
            "required_glyph_count": plan["required_glyph_count"],
            "slot_rom_range_used": [fmt(min(slot_offsets)), fmt(max(slot_offsets) + CHR_TILE_SIZE - 1)] if slot_offsets else None,
            "tile_range_used": [f"0x{min(slot_tiles):03X}", f"0x{max(slot_tiles):03X}"] if slot_tiles else None,
            "duplicate_planned_prg_bytes": duplicate_prg_bytes,
            "v02_diff": v02_summary,
            "v04_diff": v04_summary,
            "v02_report_glyphs_written": v02_report.get("glyphs_written"),
            "v02_report_changed_bytes": v02_report.get("changed_bytes"),
            "v02_report_escaped_chr_bank7_bytes": v02_report.get("escaped_chr_bank7_bytes"),
            "v04_applied_prg_targets": v04_report.get("applied_count"),
            "v04_skipped_prg_targets": v04_report.get("skipped_count"),
        },
        "slots": slots,
        "v04_prg_changed_ranges": [[fmt(start), fmt(end)] for start, end in v04_prg_ranges],
        "v04_chr_bank7_changed_ranges": [[fmt(start), fmt(end)] for start, end in v04_chr_ranges],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# CHR Bank 07 Plan Status",
        "",
        "This report validates the compact Korean glyph slot allocation and the CHR-byte footprint of the current generated ROMs.",
        "",
        "## Summary",
        "",
        f"- CHR Bank 07 ROM range: `{fmt(CHR_BANK7_START)}-{fmt(CHR_BANK7_END - 1)}`",
        f"- Planned patch tile range: `{plan['patch_tile_range'][0]}-{plan['patch_tile_range'][1]}`",
        f"- Planned patch ROM range: `{fmt(patch_slot_start)}-{fmt(patch_slot_end)}`",
        f"- Required Korean glyphs: **{plan['required_glyph_count']} / {plan['available_slots']}** available slots",
        f"- Actually used slot range: `{payload['summary']['tile_range_used'][0]}-{payload['summary']['tile_range_used'][1]}` / `{payload['summary']['slot_rom_range_used'][0]}-{payload['summary']['slot_rom_range_used'][1]}`",
        f"- Duplicate planned PRG bytes: **{len(duplicate_prg_bytes)}**",
        "",
        "## ROM Diff Validation",
        "",
        "| ROM | total changed bytes | changed range | CHR Bank7 bytes | CHR Bank7 range | pre-Bank7 bytes | post-Bank7 bytes | escaped font bytes |",
        "| --- | ---: | --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for name, summary in (("v0.2 CHR-only", v02_summary), ("v0.4 PRG+CHR", v04_summary)):
        lines.append(
            f"| {name} | {summary['changed_bytes']} | `{summary['changed_range'][0]}-{summary['changed_range'][1]}` | "
            f"{summary['chr_bank7_changed_bytes']} | `{summary['chr_bank7_changed_range'][0]}-{summary['chr_bank7_changed_range'][1]}` | "
            f"{summary['pre_chr_bank7_changed_bytes']} | {summary['post_chr_bank7_changed_bytes']} | {summary['escaped_chr_bank7_font_bytes']} |"
        )

    lines += [
        "",
        "## Required Glyph Slots",
        "",
        "| glyph | tile | ROM offset | planned PRG byte | used by labels |",
        "| --- | --- | --- | --- | --- |",
    ]
    for slot in slots:
        labels = ", ".join(f"`{label}`" for label in slot.get("used_by_labels", []))
        lines.append(
            f"| {slot['glyph']} | `{slot['tile']}` | `{slot['rom_offset']}` | `{slot['prg_plus_0x7a_byte']}` | {labels} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- `escaped font bytes` must remain `0`; otherwise a CHR patch wrote outside CHR Bank 07.",
        "- v0.4 intentionally has PRG changes before CHR Bank 07 because it includes equal-length PRG text experiments in addition to the CHR font plan.",
        "- Planned PRG bytes are valid for renderer paths that use `CHR tile = PRG byte + 0x7A`; shifted-low candidates still need runtime confirmation before final patching.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        f"glyphs={plan['required_glyph_count']} "
        f"v02_changed={v02_summary['changed_bytes']} "
        f"v04_changed={v04_summary['changed_bytes']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

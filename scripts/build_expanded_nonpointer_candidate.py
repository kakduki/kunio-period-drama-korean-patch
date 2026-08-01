#!/usr/bin/env python3
"""Build the nine selected equal-length non-pointer candidates on the full ROM."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_patch import make_records, write_ips
from rom_utils import REPO_ROOT


DEFAULT_INPUT = REPO_ROOT / "output" / "full_korean_candidate" / "kunio_period_drama_korean_full_candidate.nes"
DEFAULT_FONT = REPO_ROOT / "output" / "kunio_period_drama_korean_font_expansion_v0.5_batch32.nes"
DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "expanded_nonpointer_korean_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "expanded_nonpointer_korean_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "expanded_nonpointer_korean_candidate.md"
OUT_STEM = "kunio_period_drama_korean_expanded_nonpointer_candidate"

SELECTED_TARGETS = (
    (0x0561A, "Hashi", bytes.fromhex("96 88"), bytes.fromhex("8B 8C")),
    (0x0562F, "Tatsuichi", bytes.fromhex("90 92 82 91"), bytes.fromhex("89 98 8E 90")),
    (0x05643, "Heishichi", bytes.fromhex("9D 82 8C 91"), bytes.fromhex("8D 8E 8F 90")),
    (0x0569D, "Hashi", bytes.fromhex("A0 92"), bytes.fromhex("8B 8C")),
    (0x056DA, "Hashi", bytes.fromhex("9A 8C"), bytes.fromhex("8B 8C")),
    (0x0571C, "Hashi", bytes.fromhex("92 84"), bytes.fromhex("8B 8C")),
    (0x057D4, "Hashi", bytes.fromhex("A6 98"), bytes.fromhex("8B 8C")),
    (0x0736A, "Raifu", bytes.fromhex("BB 95 AF"), bytes.fromhex("96 8E 97")),
    (0x0739D, "Raifu", bytes.fromhex("BB 95 AF"), bytes.fromhex("96 8E 97")),
)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()[:16]


def build(
    input_rom: Path,
    font_rom: Path,
    plan_path: Path,
    output_dir: Path,
    report_json: Path,
    report_markdown: Path,
) -> dict[str, object]:
    original = input_rom.read_bytes()
    font = font_rom.read_bytes()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    patched = bytearray(original)
    targets: list[dict[str, object]] = []

    for offset, label, expected, replacement in SELECTED_TARGETS:
        current = original[offset : offset + len(expected)]
        if current != expected:
            raise ValueError(
                f"{label} target 0x{offset:05X} has {current.hex(' ').upper()}, "
                f"expected {expected.hex(' ').upper()}"
            )
        if len(expected) != len(replacement):
            raise ValueError(f"{label} target is not equal length")
        patched[offset : offset + len(replacement)] = replacement
        targets.append(
            {
                "label": label,
                "rom_offset": f"0x{offset:05X}",
                "old_bytes": expected.hex(" ").upper(),
                "new_bytes": replacement.hex(" ").upper(),
                "length": len(replacement),
                "evidence": "real frame-883 dialogue screen target record",
            }
        )

    glyphs: list[dict[str, object]] = []
    for slot in plan["slots"]:
        offset = int(str(slot["rom_offset"]), 16)
        old = bytes(original[offset : offset + 0x10])
        new = bytes(font[offset : offset + 0x10])
        if len(new) != 0x10:
            raise ValueError(f"font source slot is incomplete at 0x{offset:05X}")
        patched[offset : offset + 0x10] = new
        glyphs.append(
            {
                "glyph": slot["glyph"],
                "tile": slot["tile"],
                "rom_offset": f"0x{offset:05X}",
                "old_sha1_16": sha1(old),
                "new_sha1_16": sha1(new),
            }
        )

    patched_bytes = bytes(patched)
    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"{OUT_STEM}.nes"
    ips_path = output_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(patched_bytes)
    records = make_records(original, patched_bytes)
    write_ips(ips_path, records)
    if apply_ips(original, ips_path) != patched_bytes:
        raise AssertionError("expanded non-pointer candidate IPS round trip failed")

    payload: dict[str, object] = {
        "status": "BUILT_RUNTIME_VISUAL_PENDING",
        "input_rom": str(input_rom),
        "font_source_rom": str(font_rom),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "input_md5": md5(original),
        "font_source_md5": md5(font),
        "candidate_md5": md5(patched_bytes),
        "selected_target_count": len(targets),
        "targets": targets,
        "glyph_slot_count": len(glyphs),
        "glyph_slots": glyphs,
        "ips_records": len(records),
        "visual_route": "kunio_input_explorer_v042, frame-883 target family",
        "release_status": "NOT_READY",
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Expanded Non-Pointer Korean Candidate",
        "",
        "Candidate built from the full pointer/menu ROM using nine equal-length PRG targets and the 18 allocated 8x8 Korean glyph slots.",
        "",
        f"- Input MD5: `{payload['input_md5']}`.",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Selected PRG targets: `{payload['selected_target_count']}`.",
        f"- Korean glyph slots copied: `{payload['glyph_slot_count']}`.",
        f"- IPS records: `{payload['ips_records']}`.",
        "- Build status: `PASS`; IPS round trip: `PASS`.",
        "- Visual status: pending the bounded frame-883 route on this composed candidate.",
        "- Release status: `NOT_READY`.",
        "",
        "## PRG Targets",
        "",
        "| label | ROM offset | old bytes | new bytes | evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {row['label']} | {row['rom_offset']} | {row['old_bytes']} | {row['new_bytes']} | {row['evidence']} |"
        for row in targets
    )
    lines += [
        "",
        "## Interpretation",
        "",
        "The nine PRG spans are equal-length and were observed in the real frame-883 dialogue target record set. This candidate still needs exact screenshot/PPU proof on the composed ROM and does not prove the natural boss route.",
        "",
    ]
    report_markdown.write_text("\n".join(lines), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--font-rom", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()
    payload = build(
        args.input_rom,
        args.font_rom,
        args.plan,
        args.out_dir,
        args.report_json,
        args.report_markdown,
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

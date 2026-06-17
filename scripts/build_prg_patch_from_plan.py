#!/usr/bin/env python3
"""Build an experimental ROM with planned CHR glyphs plus safe PRG text edits.

Only equal-length runtime-confirmed text targets are patched by default. Targets
that need shortening or padding are reported but left untouched until the table
control/padding rules are confirmed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from rom_utils import REPO_ROOT, find_rom_path


DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
DEFAULT_FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_plan_v0.2.nes"
DEFAULT_OUT_DIR = REPO_ROOT / "output"
OUT_STEM = "kunio_period_drama_korean_prg_plan_v0.3"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def parse_byte_list(values: list[str]) -> bytes:
    return bytes(int(value, 16) for value in values)


def parse_hex_bytes(text: str) -> bytes:
    return bytes(int(part, 16) for part in text.split() if part)


def build_prg_patch(
    original_rom_path: Path,
    font_rom_path: Path,
    plan_path: Path,
    out_dir: Path,
    *,
    include_evidence: set[str],
) -> dict[str, object]:
    original = original_rom_path.read_bytes()
    patched = bytearray(font_rom_path.read_bytes())
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    applied: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for target in plan["targets"]:
        evidence = str(target.get("evidence_level", ""))
        if evidence not in include_evidence:
            skipped.append({
                "label": target.get("label"),
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "reason": f"evidence level {evidence!r} not selected",
            })
            continue

        planned = parse_byte_list(list(target.get("planned_prg_bytes", [])))
        original_expected = parse_hex_bytes(str(target.get("original_expected_bytes", "")))
        rom_hit = int(str(target["rom_hit"]), 16)
        current = bytes(original[rom_hit:rom_hit + len(original_expected)])

        if not planned:
            skipped.append({
                "label": target.get("label"),
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "reason": "no planned PRG bytes",
            })
            continue
        if current != original_expected:
            skipped.append({
                "label": target.get("label"),
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "reason": f"ROM bytes {current.hex(' ').upper()} do not match expected {original_expected.hex(' ').upper()}",
            })
            continue
        if len(planned) != len(original_expected):
            skipped.append({
                "label": target.get("label"),
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "reason": f"length mismatch planned={len(planned)} original={len(original_expected)}",
            })
            continue

        patched[rom_hit:rom_hit + len(planned)] = planned
        applied.append({
            "label": target.get("label"),
            "rom_hit": target.get("rom_hit"),
            "source": target.get("source"),
            "korean": target.get("korean"),
            "old_bytes": original_expected.hex(" ").upper(),
            "new_bytes": planned.hex(" ").upper(),
            "evidence_level": evidence,
        })

    records = make_records(original, bytes(patched))
    out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = out_dir / f"{OUT_STEM}.ips"
    patched_path = out_dir / f"{OUT_STEM}.nes"
    report_path = out_dir / f"{OUT_STEM}_build_report.json"

    write_ips(ips_path, records)
    patched_path.write_bytes(patched)

    changed_offsets = [
        offset for offset, (a, b) in enumerate(zip(original, patched)) if a != b
    ]
    report = {
        "plan": str(plan_path),
        "font_rom": str(font_rom_path),
        "original_rom": str(original_rom_path),
        "original_md5": md5(original),
        "patched_md5": md5(bytes(patched)),
        "patched_rom_path": str(patched_path),
        "ips_path": str(ips_path),
        "include_evidence": sorted(include_evidence),
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "changed_bytes_total": len(changed_offsets),
        "changed_rom_range": [
            f"0x{min(changed_offsets):05X}",
            f"0x{max(changed_offsets):05X}",
        ] if changed_offsets else [],
        "ips_records": len(records),
        "applied": applied,
        "skipped": skipped,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Optional original .nes path; defaults to rom/*.nes")
    parser.add_argument("--font-rom", default=str(DEFAULT_FONT_ROM))
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument(
        "--include-evidence",
        default="runtime-confirmed",
        help="Comma-separated evidence levels to patch.",
    )
    args = parser.parse_args()

    original_rom = Path(args.rom).expanduser().resolve() if args.rom else find_rom_path()
    font_rom = Path(args.font_rom).expanduser().resolve()
    plan = Path(args.plan).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    include_evidence = {part.strip() for part in args.include_evidence.split(",") if part.strip()}

    report = build_prg_patch(original_rom, font_rom, plan, out_dir, include_evidence=include_evidence)
    print(f"patched ROM: {report['patched_rom_path']}")
    print(f"IPS: {report['ips_path']}")
    print(f"applied={report['applied_count']} skipped={report['skipped_count']} changed_bytes={report['changed_bytes_total']}")
    print(f"patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build FCEUX-only ROMs for PRG padding strategy experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from rom_utils import REPO_ROOT, find_rom_path


DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "prg_padding_experiment_plan.json"
DEFAULT_FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_plan_v0.2.nes"
DEFAULT_OUT_DIR = REPO_ROOT / "output"
OUT_STEM = "kunio_period_drama_korean_prg_padding_exp"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def parse_bytes(text: str) -> bytes:
    return bytes(int(part, 16) for part in str(text).split() if part)


def build_one(
    original: bytes,
    base: bytes,
    row: dict,
    strategy: dict,
    out_dir: Path,
    out_stem: str,
) -> dict:
    patched = bytearray(base)
    rom_hit = int(str(row["rom_hit"]), 16)
    original_bytes = parse_bytes(row["original_bytes"])
    patched_bytes = parse_bytes(strategy["patched_bytes"])
    if len(original_bytes) != len(patched_bytes):
        raise RuntimeError(
            f"Strategy {strategy['strategy']} for {row['label']} changes span length "
            f"{len(original_bytes)} -> {len(patched_bytes)}"
        )
    current = original[rom_hit:rom_hit + len(original_bytes)]
    if current != original_bytes:
        raise RuntimeError(
            f"Base ROM bytes at 0x{rom_hit:05X} are {current.hex(' ').upper()}, "
            f"expected {original_bytes.hex(' ').upper()}"
        )

    patched[rom_hit:rom_hit + len(patched_bytes)] = patched_bytes
    records = make_records(original, bytes(patched))
    strategy_name = str(strategy["strategy"])
    rom_path = out_dir / f"{out_stem}_{row['label']}_{strategy_name}.nes"
    ips_path = out_dir / f"{out_stem}_{row['label']}_{strategy_name}.ips"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)

    changed_offsets = [
        offset for offset, (a, b) in enumerate(zip(original, patched)) if a != b
    ]
    return {
        "label": row["label"],
        "rom_hit": row["rom_hit"],
        "source": row["source"],
        "source_romaji": row.get("source_romaji", ""),
        "korean": row["korean"],
        "strategy": strategy_name,
        "original_bytes": row["original_bytes"],
        "patched_bytes": strategy["patched_bytes"],
        "pad_bytes": strategy["pad_bytes"],
        "changes_original_tail": strategy["changes_original_tail"],
        "rom_path": str(rom_path),
        "ips_path": str(ips_path),
        "patched_md5": md5(bytes(patched)),
        "changed_bytes_total": len(changed_offsets),
        "changed_rom_range": [
            f"0x{min(changed_offsets):05X}",
            f"0x{max(changed_offsets):05X}",
        ] if changed_offsets else [],
        "ips_records": len(records),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Optional original .nes path; defaults to rom/*.nes")
    parser.add_argument("--rom", dest="rom_option", help="Optional original .nes path; overrides the positional rom argument.")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--font-rom", default=str(DEFAULT_FONT_ROM))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--out-stem", default=OUT_STEM)
    parser.add_argument(
        "--target-label",
        default="",
        help="Optional single experiment label. Defaults to all runtime-confirmed first targets.",
    )
    args = parser.parse_args()

    rom_arg = args.rom_option or args.rom
    original_rom = find_rom_path(rom_arg).resolve()
    plan_path = Path(args.plan).expanduser().resolve()
    font_rom = Path(args.font_rom).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    original = original_rom.read_bytes()
    base = font_rom.read_bytes()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = list(plan.get("runtime_confirmed_first_targets", []))
    if args.target_label:
        rows = [row for row in rows if row.get("label") == args.target_label]
    if not rows:
        raise RuntimeError("No matching runtime-confirmed padding experiment targets")

    builds = []
    for row in rows:
        for strategy in row.get("strategies", []):
            builds.append(build_one(original, base, row, strategy, out_dir, args.out_stem))

    report = {
        "plan": str(plan_path),
        "font_rom": str(font_rom),
        "original_rom": str(original_rom),
        "original_md5": md5(original),
        "font_rom_md5": md5(base),
        "out_stem": args.out_stem,
        "target_count": len(rows),
        "build_count": len(builds),
        "builds": builds,
        "warning": "These ROMs are FCEUX-only padding experiments, not final patch candidates.",
    }
    report_path = out_dir / f"{args.out_stem}_build_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"report: {report_path}")
    print(f"targets={len(rows)} builds={len(builds)}")
    for build in builds:
        print(f"{build['strategy']}: {build['rom_path']} md5={build['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

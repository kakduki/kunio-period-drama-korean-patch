#!/usr/bin/env python3
"""Generate runtime targets for control-free English pre-pointer records."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_SCRIPT = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_ROM = REPO_ROOT / "output" / "full_korean_expanded_candidate" / "kunio_period_drama_korean_expanded_candidate.nes"
DEFAULT_OUTPUT = REPO_ROOT / "lua" / "kunio_pre_pointer_runtime_targets.lua"
DEFAULT_REPORT = REPO_ROOT / "rom_analysis" / "pre_pointer_runtime_targets.json"
CONTROL_RE = re.compile(r"<([0-9A-Fa-f]{2})>")
BANK1_PRG_START = 0x4010
CPU_BASE = 0x8000


def generate(script_path: Path, rom_path: Path, output_path: Path, report_path: Path) -> dict[str, object]:
    rom = rom_path.read_bytes()
    targets: list[dict[str, object]] = []
    skipped: dict[str, int] = {}
    with script_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if not row["record_id"].startswith("EN-PRE-"):
                continue
            controls = [token for token in CONTROL_RE.findall(row["en_text"]) if token.upper() != "FF"]
            if controls:
                skipped["control_skeleton"] = skipped.get("control_skeleton", 0) + 1
                continue
            if "<FF>" not in row["en_text"]:
                skipped["unterminated"] = skipped.get("unterminated", 0) + 1
                continue
            offset = int(row["en_rom_offset"], 16)
            raw = bytes.fromhex(row["en_raw_bytes"])
            current = rom[offset : offset + len(raw)]
            if len(current) != len(raw):
                skipped["short_rom"] = skipped.get("short_rom", 0) + 1
                continue
            cpu_addr = CPU_BASE + offset - BANK1_PRG_START
            if not 0x8000 <= cpu_addr <= 0xBFFF:
                skipped["cpu_window"] = skipped.get("cpu_window", 0) + 1
                continue
            targets.append({
                "id": row["record_id"],
                "rom_offset": f"0x{offset:05X}",
                "cpu_addr": f"0x{cpu_addr:04X}",
                "bytes": current.hex(" ").upper(),
                "english_bytes": raw.hex(" ").upper(),
                "english_text": row["en_text"],
                "context": row["context"],
            })

    lines = [
        "-- Generated from the English pre-pointer script dump and the runnable pointer-owner candidate.",
        "return {",
    ]
    for target in targets:
        values = "{" + ",".join(f"0x{value:02X}" for value in bytes.fromhex(target["bytes"])) + "}"
        lines.append(
            "  { id = " + json.dumps(target["id"])
            + ", rom_offset = " + json.dumps(target["rom_offset"])
            + ", cpu_addr = " + target["cpu_addr"]
            + ", bytes = " + values + " },"
        )
    lines.append("}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "status": "GENERATED_PRE_POINTER_RUNTIME_TARGETS",
        "script_dump": str(script_path),
        "candidate_rom": str(rom_path),
        "target_count": len(targets),
        "targets": targets,
        "skipped": skipped,
        "mapping": {
            "rom_bank_start": f"0x{BANK1_PRG_START:04X}",
            "cpu_base": f"0x{CPU_BASE:04X}",
            "formula": "CPU = 0x8000 + (ROM offset - 0x4010)",
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    payload = generate(args.script.resolve(), args.rom.resolve(), args.output.resolve(), args.report.resolve())
    print(json.dumps({"status": payload["status"], "target_count": payload["target_count"], "skipped": payload["skipped"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a no-font structural probe for one pre-pointer record.

The probe preserves the record width and terminator but replaces its payload
with the already-owned glyph codes ``0x84 0x89``.  It is
only useful for route regression triage; it is not a translation candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from rom_utils import REPO_ROOT


DEFAULT_INPUT = REPO_ROOT / "output" / "full_korean_expanded_candidate" / "kunio_period_drama_korean_expanded_candidate.nes"
DEFAULT_TARGETS = REPO_ROOT / "rom_analysis" / "pre_pointer_runtime_targets.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "pre_pointer_structural_probes"
DEFAULT_REPORT_DIR = REPO_ROOT / "rom_analysis" / "pre_pointer_structural_probes"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def build(input_rom: Path, targets_path: Path, record_id: str, output_dir: Path, report_dir: Path) -> dict[str, object]:
    source = input_rom.read_bytes()
    targets = json.loads(targets_path.read_text(encoding="utf-8"))["targets"]
    target = next((row for row in targets if row["id"] == record_id), None)
    if target is None:
        raise ValueError(f"unknown target: {record_id}")
    offset = int(str(target["rom_offset"]), 16)
    raw = bytes.fromhex(str(target["bytes"]))
    if not raw.endswith(b"\xFF") or len(raw) < 3:
        raise ValueError(f"target is not a payload record: {record_id}")
    width = len(raw) - 1
    payload = bytes([0x84, 0x89]) + bytes([0xFF]) * (width - 2)
    candidate = bytearray(source)
    candidate[offset : offset + width] = payload
    candidate[offset + width] = 0xFF
    candidate_bytes = bytes(candidate)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = f"kunio_period_drama_korean_structural_probe_{record_id.lower()}"
    rom_path = output_dir / f"{stem}.nes"
    ips_path = output_dir / f"{stem}.ips"
    report_path = report_dir / f"{record_id}.json"
    rom_path.write_bytes(candidate_bytes)
    write_ips(ips_path, make_records(source, candidate_bytes))
    report = {
        "status": "BUILT_PRE_POINTER_STRUCTURAL_PROBE",
        "release_status": "NOT_READY",
        "input_rom": str(input_rom),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "record_id": record_id,
        "rom_offset": target["rom_offset"],
        "cpu_addr": target["cpu_addr"],
        "original_bytes": target["bytes"],
        "probe_bytes": payload.hex(" ").upper(),
        "candidate_md5": md5(candidate_bytes),
        "purpose": "Route-regression triage only; not a translated or release candidate.",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record_id")
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args()
    report = build(args.input_rom.resolve(), args.targets.resolve(), args.record_id, args.output_dir.resolve(), args.report_dir.resolve())
    print(json.dumps({"status": report["status"], "record_id": report["record_id"], "candidate_md5": report["candidate_md5"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extract a structural catalog and raw pointer candidates from the Japanese ROM."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SIZE = 262_160
EXPECTED_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
POINTER_TABLE_OFFSET = 0x05DD4
POINTER_COUNT = 248
CPU_WINDOW_START = 0x8000
FILE_WINDOW_START = 0x4010
CONTROL_CANDIDATES = {0x00, 0xBB, 0xCA, 0xF8, 0xFF}


def verify_base(path: Path) -> bytes:
    if not path.is_file():
        raise SystemExit(f"base ROM not found: {path}")
    data = path.read_bytes()
    digest = hashlib.md5(data).hexdigest()
    if len(data) != EXPECTED_SIZE or digest != EXPECTED_MD5:
        raise SystemExit(
            f"unexpected base ROM: size={len(data)} md5={digest}; "
            f"expected size={EXPECTED_SIZE} md5={EXPECTED_MD5}"
        )
    return data


def raw_pointer_rows(data: bytes) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(POINTER_COUNT):
        pointer_offset = POINTER_TABLE_OFFSET + index * 2
        raw_pointer = data[pointer_offset : pointer_offset + 2]
        if len(raw_pointer) != 2:
            break
        cpu = raw_pointer[0] | (raw_pointer[1] << 8)
        target = FILE_WINDOW_START + (cpu - CPU_WINDOW_START) if cpu >= CPU_WINDOW_START else None
        row: dict[str, object] = {
            "id": f"PTR-{index:03d}",
            "category": "pointer_dialogue",
            "bank": 1,
            "pointer_address": f"0x{pointer_offset:05X}",
            "text_address": f"0x{target:05X}" if target is not None else "UNKNOWN",
            "original_bytes": "",
            "original_text": "UNKNOWN",
            "translated_text": "",
            "control_codes": "",
            "max_bytes": "UNKNOWN",
            "speaker": "UNKNOWN",
            "scene": "UNKNOWN",
            "notes": "",
            "cpu_address": f"0x{cpu:04X}",
            "termination_status": "UNKNOWN",
        }
        if target is None or target < 0 or target >= len(data):
            row["notes"] = "Pointer does not map into the declared CPU window/file."
            rows.append(row)
            continue
        limit = min(len(data), target + 0x0200)
        end = data.find(b"\xFF", target, limit)
        if end < 0:
            end = limit
            row["termination_status"] = "UNTERMINATED_WITHIN_0x200"
            row["notes"] = "Raw candidate capped at 0x200 bytes; no termination claim."
        else:
            end += 1
            row["termination_status"] = "HEURISTIC_FIRST_FF"
            row["notes"] = "First 0xFF boundary only; runtime source-read is required before patching."
        payload = data[target:end]
        row["original_bytes"] = payload.hex(" ")
        row["control_codes"] = " ".join(f"{value:02X}" for value in payload if value in CONTROL_CANDIDATES)
        row["max_bytes"] = len(payload)
        rows.append(row)
    return rows


def write_raw_catalog(data: bytes, output_dir: Path) -> None:
    rows = raw_pointer_rows(data)
    fields = [
        "id", "category", "bank", "pointer_address", "text_address", "original_bytes",
        "original_text", "translated_text", "control_codes", "max_bytes", "speaker",
        "scene", "notes", "cpu_address", "termination_status",
    ]
    with (output_dir / "extracted_text.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "base": {"size": len(data), "md5": hashlib.md5(data).hexdigest()},
        "pointer_table_offset": f"0x{POINTER_TABLE_OFFSET:05X}",
        "pointer_count": len(rows),
        "cpu_window": f"0x{CPU_WINDOW_START:04X}-0x{CPU_WINDOW_START + 0x3FFF:04X}",
        "file_window_start": f"0x{FILE_WINDOW_START:05X}",
        "termination_policy": "first 0xFF is a heuristic boundary only; no encoding or scene meaning is inferred",
        "rows": rows,
    }
    (output_dir / "extracted_text.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"raw_pointer_rows={len(rows)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True, help="verified Japanese base ROM")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "rom_analysis")
    args = parser.parse_args()

    rom = args.rom if args.rom.is_absolute() else ROOT / args.rom
    data = verify_base(rom)
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "scripts" / "build_pointer_dialogue_catalog.py"),
        "--english-dump",
        str(ROOT / "rom_analysis" / "english_script_dump.tsv"),
        "--conservative-catalog",
        str(ROOT / "rom_analysis" / "pointer_dialogue_catalog.tsv"),
        "--output-tsv",
        str(out / "pointer_dialogue_catalog.tsv"),
        "--output-json",
        str(out / "pointer_dialogue_catalog.json"),
        "--output-markdown",
        str(out / "pointer_dialogue_catalog.md"),
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    write_raw_catalog(data, out)
    print(f"extracted structural catalog: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
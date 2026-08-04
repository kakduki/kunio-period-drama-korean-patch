#!/usr/bin/env python3
"""Decode a declared little-endian pointer table with explicit bank context."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("--table-offset", type=lambda value: int(value, 0), default=0x5DD4)
    parser.add_argument("--count", type=int, default=248)
    parser.add_argument("--cpu-window-start", type=lambda value: int(value, 0), default=0x8000)
    parser.add_argument("--file-window-start", type=lambda value: int(value, 0), default=0x4010)
    parser.add_argument("--output-dir", type=Path, default=Path("rom_analysis/pointer_scan"))
    args = parser.parse_args()
    data = args.rom.resolve().read_bytes()
    rows: list[dict[str, object]] = []
    for index in range(args.count):
        offset = args.table_offset + index * 2
        raw = data[offset : offset + 2]
        if len(raw) != 2:
            break
        cpu = raw[0] | (raw[1] << 8)
        target = args.file_window_start + (cpu - args.cpu_window_start) if cpu >= args.cpu_window_start else None
        rows.append(
            {
                "index": index,
                "table_file_offset": f"0x{offset:06X}",
                "raw_pointer": raw.hex(" "),
                "cpu_address": f"0x{cpu:04X}",
                "active_cpu_window": f"0x{args.cpu_window_start:04X}-0x{args.cpu_window_start + 0x3FFF:04X}",
                "file_target_offset": f"0x{target:06X}" if target is not None else "UNMAPPED",
                "target_in_file": target is not None and 0 <= target < len(data),
            }
        )
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "table_file_offset": f"0x{args.table_offset:06X}",
        "count_requested": args.count,
        "count_decoded": len(rows),
        "pointer_width": 2,
        "endianness": "little",
        "active_bank_context": "declared Bank 1 CPU window; verify mapper state before reuse",
        "rows": rows,
    }
    (output / "pointer_candidates.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (output / "pointer_candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["index", "table_file_offset", "raw_pointer", "cpu_address", "active_cpu_window", "file_target_offset", "target_in_file"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"pointers={len(rows)}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

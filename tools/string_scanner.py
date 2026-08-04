#!/usr/bin/env python3
"""Find byte runs that are candidates for game-specific text tokens.

This scanner deliberately reports byte candidates only. It does not claim
Shift-JIS, Japanese Unicode, or a final game encoding without runtime proof.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def parse_codes(spec: str) -> set[int]:
    values: set[int] = set()
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            values.update(range(int(left, 16), int(right, 16) + 1))
        else:
            values.add(int(token, 16))
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("--start", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--end", type=lambda value: int(value, 0))
    parser.add_argument("--codes", default="81-9A,00,BB,CA,F8,FF")
    parser.add_argument("--min-length", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=Path("rom_analysis/string_scan"))
    args = parser.parse_args()
    data = args.rom.resolve().read_bytes()
    start = max(0, args.start)
    end = min(len(data), args.end if args.end is not None else len(data))
    allowed = parse_codes(args.codes)
    runs: list[dict[str, object]] = []
    run_start: int | None = None
    for offset in range(start, end):
        if data[offset] in allowed:
            if run_start is None:
                run_start = offset
        elif run_start is not None:
            if offset - run_start >= args.min_length:
                payload = data[run_start:offset]
                runs.append({"offset": run_start, "length": len(payload), "bytes": payload.hex(" "), "encoding_status": "UNRESOLVED"})
            run_start = None
    if run_start is not None and end - run_start >= args.min_length:
        payload = data[run_start:end]
        runs.append({"offset": run_start, "length": len(payload), "bytes": payload.hex(" "), "encoding_status": "UNRESOLVED"})
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "string_candidates.json").write_text(json.dumps({"codes": sorted(allowed), "runs": runs}, indent=2) + "\n", encoding="utf-8")
    with (output / "string_candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["offset", "length", "bytes", "encoding_status"])
        writer.writeheader()
        writer.writerows(runs)
    print(f"candidates={len(runs)}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

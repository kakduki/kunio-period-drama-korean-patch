#!/usr/bin/env python3
"""Summarize bounded FCEUX RAM write traces after combat entry."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--start-frame", type=int, default=900)
    parser.add_argument("--top", type=int, default=80)
    args = parser.parse_args()

    rows = []
    with args.trace.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            frame = int(row["frame"])
            address = int(row["address"], 16)
            value = int(row["value"], 16)
            if frame >= args.start_frame:
                rows.append((frame, address, value))

    counts = Counter(address for _, address, _ in rows)
    values: dict[int, set[int]] = defaultdict(set)
    first_last: dict[int, list[int]] = {}
    for frame, address, value in rows:
        values[address].add(value)
        first_last.setdefault(address, [frame, frame])
        first_last[address][1] = frame

    print(f"rows_after_frame={len(rows)} addresses={len(counts)}")
    print("address\twrites\tunique_values\tfirst_frame\tlast_frame\tvalues")
    for address, count in counts.most_common(args.top):
        value_text = " ".join(f"{value:02X}" for value in sorted(values[address]))
        first, last = first_last[address]
        print(f"{address:04X}\t{count}\t{len(values[address])}\t{first}\t{last}\t{value_text}")

    print("\nobject_or_runtime_candidates")
    for address, count in counts.most_common():
        if not (0x0200 <= address <= 0x05FF or 0x0700 <= address <= 0x07FF):
            continue
        value_text = " ".join(f"{value:02X}" for value in sorted(values[address]))
        first, last = first_last[address]
        print(f"{address:04X}\t{count}\t{first}-{last}\t{value_text}")


if __name__ == "__main__":
    main()

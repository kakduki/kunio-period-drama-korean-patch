#!/usr/bin/env python3
"""Rank RAM addresses that change at the bounded combat screen transition."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def load_snapshots(root: Path) -> list[tuple[int, bytes]]:
    rows = []
    for path in sorted(root.glob("frame_*_cpu_ram.bin")):
        match = re.match(r"frame_(\d+)_cpu_ram\.bin$", path.name)
        if match:
            rows.append((int(match.group(1)), path.read_bytes()))
    return rows


def print_candidates(rows: list[tuple[int, bytes]], start: int, end: int) -> None:
    frames = [frame for frame, _ in rows]
    print("frames=" + ",".join(str(frame) for frame in frames))
    print(f"range=${start:04X}-${end - 1:04X}")
    if len(rows) < 4:
        return
    split = max(1, len(rows) - 2)
    print("transition_candidates")
    for address in range(start, end):
        values = [ram[address] for _, ram in rows]
        before = values[:split]
        after = values[split:]
        if len(set(before)) <= 4 and len(set(after)) <= 4 and before[-1] != after[0]:
            print(f"{address:04X} " + " ".join(f"{value:02X}" for value in values))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--start", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--end", type=lambda value: int(value, 0), default=0x800)
    args = parser.parse_args()
    rows = load_snapshots(args.root)
    if not rows:
        raise SystemExit(f"no CPU RAM snapshots under {args.root}")
    print_candidates(rows, args.start, args.end)


if __name__ == "__main__":
    main()

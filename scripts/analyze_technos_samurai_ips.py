#!/usr/bin/env python3
"""Produce a conservative, reproducible structural map of the English IPS.

This script labels only physical NES regions.  It deliberately does not claim that
any PRG range is a pointer table without runtime evidence from the renderer trace.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

HEADER_SIZE = 16


def parse_ips(data: bytes) -> list[tuple[int, bytes]]:
    if not data.startswith(b"PATCH") or not data.endswith(b"EOF"):
        raise ValueError("not a complete IPS file")
    index, records = 5, []
    while data[index : index + 3] != b"EOF":
        offset = int.from_bytes(data[index : index + 3], "big")
        size = int.from_bytes(data[index + 3 : index + 5], "big")
        index += 5
        if size == 0:
            repeat = int.from_bytes(data[index : index + 2], "big")
            payload = data[index + 2 : index + 3] * repeat
            index += 3
        else:
            payload = data[index : index + size]
            index += size
        records.append((offset, payload))
    return records


def region(offset: int, prg_end: int, rom_size: int) -> str:
    if offset < HEADER_SIZE:
        return "header"
    if offset < prg_end:
        return "prg"
    if offset < rom_size:
        return "chr"
    return "out_of_rom"


def merged_runs(offsets: list[int]) -> list[tuple[int, int]]:
    if not offsets:
        return []
    runs, start, previous = [], offsets[0], offsets[0]
    for offset in offsets[1:]:
        if offset != previous + 1:
            runs.append((start, previous + 1))
            start = offset
        previous = offset
    runs.append((start, previous + 1))
    return runs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, default=Path("rom/kunio.nes"))
    parser.add_argument("--ips", type=Path, default=Path("reference/technos-samurai-v1/TSe-v10.ips"))
    parser.add_argument("--output", type=Path, default=Path("analysis/english_reference_structure.json"))
    args = parser.parse_args()

    base = args.rom.read_bytes()
    ips = args.ips.read_bytes()
    if len(base) < HEADER_SIZE or base[:4] != b"NES\x1a":
        raise ValueError("base ROM has no iNES header")
    prg_end = HEADER_SIZE + base[4] * 16_384
    rom_size = len(base)
    patched = bytearray(base)
    records = parse_ips(ips)
    record_regions, changed = Counter(), []
    for offset, payload in records:
        record_regions[region(offset, prg_end, rom_size)] += 1
        if offset + len(payload) > len(patched):
            raise ValueError(f"record escapes ROM at 0x{offset:06X}")
        for local, value in enumerate(payload):
            absolute = offset + local
            if patched[absolute] != value:
                changed.append(absolute)
            patched[absolute] = value

    changed.sort()
    changed_regions = Counter(region(offset, prg_end, rom_size) for offset in changed)
    prg_banks = Counter((offset - HEADER_SIZE) // 8192 for offset in changed if HEADER_SIZE <= offset < prg_end)
    chr_banks = Counter((offset - prg_end) // 1024 for offset in changed if prg_end <= offset < rom_size)
    runs = merged_runs(changed)
    result = {
        "method": "physical diff only; PRG subranges are candidates, not confirmed pointer tables or code",
        "base": {"path": str(args.rom), "bytes": len(base), "md5": hashlib.md5(base).hexdigest(), "sha256": hashlib.sha256(base).hexdigest()},
        "ips": {"path": str(args.ips), "bytes": len(ips), "sha256": hashlib.sha256(ips).hexdigest(), "records": len(records)},
        "target": {"md5": hashlib.md5(patched).hexdigest(), "sha256": hashlib.sha256(patched).hexdigest()},
        "layout": {"header": [0, HEADER_SIZE], "prg": [HEADER_SIZE, prg_end], "chr": [prg_end, rom_size]},
        "records_by_start_region": dict(record_regions),
        "changed_bytes_by_region": dict(changed_regions),
        "changed_runs": [{"start": start, "end_exclusive": end, "bytes": end - start, "region": region(start, prg_end, rom_size)} for start, end in runs],
        "prg_8k_bank_changed_bytes": dict(sorted(prg_banks.items())),
        "chr_1k_bank_changed_bytes": dict(sorted(chr_banks.items())),
        "header_changes": [{"offset": offset, "before": base[offset], "after": patched[offset]} for offset in changed if offset < HEADER_SIZE],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"records": len(records), "changed": dict(changed_regions), "target_md5": result["target"]["md5"], "runs": len(runs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

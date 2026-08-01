#!/usr/bin/env python3
"""Verify the bounded FCEUX Items action-row runtime capture."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


EXPECTED_SOURCE = bytes.fromhex(
    "23 63 00 1B 8C 98 00 00 00 00 00 00 "
    "99 9B 9C 00 00 00 00 00 9E 9C 00 00 "
    "00 00 00 00 99 A3 00 23 4C"
)
EXPECTED_ACTION = bytes.fromhex("8C 98 00 99 9B 9C 9E 9C 99 A3")
QUEUE_ADDRESSES = (0x6364, 0x6365, 0x6366, 0x636C, 0x636D, 0x636E, 0x6374, 0x6375, 0x637C, 0x637D)
PPU_ADDRESSES = (0x2363, 0x2364, 0x2365, 0x236B, 0x236C, 0x236D, 0x2373, 0x2374, 0x237B, 0x237C)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def value(row: dict[str, str], key: str) -> int:
    return int(row[key], 16)


def choose_frame(rows_: list[dict[str, str]], addresses: tuple[int, ...], pc: str | None = None) -> int | None:
    for row in rows_:
        if value(row, "cpu_address" if "cpu_address" in row else "address") in addresses:
            if pc is None or row.get("pc", "").upper() == pc:
                return int(row["frame"])
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--candidate-rom", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    capture = args.capture_dir
    summary = rows(capture / "summary.tsv")
    queue = rows(capture / "queue_writes.tsv")
    ppu = rows(capture / "ppu_writes.tsv")
    mapper = rows(capture / "mapper_writes.tsv")

    source = args.candidate_rom.read_bytes()[0x13727 : 0x13727 + len(EXPECTED_SOURCE)]
    summary_pass = any(row.get("reason") == "lua_done" and row.get("detail_a", "").startswith("captured=true") for row in summary)

    queue_hits = {
        int(row["cpu_address"], 16): int(row["value"], 16)
        for row in queue
        if row.get("pc", "").upper() == "B70D"
    }
    queue_values = bytes(queue_hits.get(address, -1) for address in QUEUE_ADDRESSES)

    ppu_hits = {
        int(row["ppu_address"], 16): int(row["value"], 16)
        for row in ppu
        if int(row["frame"]) == 1736
    }
    ppu_values = bytes(ppu_hits.get(address, -1) for address in PPU_ADDRESSES)

    bank_values = [
        {"register": row.get("selected_register"), "value": row.get("value")}
        for row in mapper
        if row.get("frame") == "1736" and row.get("kind") == "MMC3_DATA"
    ]
    checks = {
        "capture_completed": summary_pass,
        "candidate_source_bytes": source == EXPECTED_SOURCE,
        "queue_action_bytes": queue_values == EXPECTED_ACTION,
        "ppu_action_bytes": ppu_values == EXPECTED_ACTION,
        "items_banks": all({"1": "3E", "6": "08", "7": "09"}[register] in {row["value"] for row in bank_values if row["register"] == register} for register in ("1", "6", "7")),
    }
    result = {
        "verdict": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "evidence": {
            "capture_frame": 1906,
            "action_frame": 1736,
            "queue_pc": "B70D",
            "queue_values": queue_values.hex(" ").upper(),
            "ppu_values": ppu_values.hex(" ").upper(),
            "items_banks": bank_values,
            "source_rom_offset": "0x13727",
        },
    }
    serialized = json.dumps(result, ensure_ascii=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
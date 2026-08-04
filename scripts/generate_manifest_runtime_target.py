#!/usr/bin/env python3
"""Generate exact FCEUX targets from relocated manifest-candidate pointers."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


POINTER_TABLE_OFFSET = 0x05DD4
POINTER_COUNT = 248
CPU_WINDOW_START = 0x8000
CPU_WINDOW_END = 0xBFFF
FILE_WINDOW_START = 0x04010
PRG_BANK_SIZE = 0x2000


def read_target(rom: bytes, pointer_index: int, max_length: int) -> dict[str, object]:
    if not 0 <= pointer_index < POINTER_COUNT:
        raise ValueError(f"pointer index outside 0-{POINTER_COUNT - 1}: {pointer_index}")
    pointer_offset = POINTER_TABLE_OFFSET + pointer_index * 2
    cpu_address = int.from_bytes(rom[pointer_offset:pointer_offset + 2], "little")
    if not CPU_WINDOW_START <= cpu_address <= CPU_WINDOW_END:
        raise ValueError(f"pointer {pointer_index} CPU address is outside Bank-1 window: 0x{cpu_address:04X}")
    record_offset = FILE_WINDOW_START + cpu_address - CPU_WINDOW_START
    if record_offset >= len(rom):
        raise ValueError(f"pointer {pointer_index} maps past candidate ROM: 0x{record_offset:05X}")
    search_end = min(len(rom), record_offset + max_length)
    terminator = rom.find(b"\xFF", record_offset, search_end)
    if terminator < 0:
        raise ValueError(f"pointer {pointer_index} has no 0xFF terminator within 0x{max_length:X} bytes")
    payload = rom[record_offset:terminator + 1]
    prg_bank = (record_offset - 0x10) // PRG_BANK_SIZE
    return {
        "pointer_index": pointer_index,
        "pointer_rom_offset": pointer_offset,
        "cpu_address": cpu_address,
        "record_rom_offset": record_offset,
        "record_end_cpu": cpu_address + len(payload) - 1,
        "prg_bank": prg_bank,
        "bytes": payload,
    }


def render_lua(rom_path: Path, rom_md5: str, targets: list[dict[str, object]]) -> str:
    lines = [
        "-- Generated from a relocated manifest candidate; do not hand-edit addresses.",
        f"-- candidate={rom_path.as_posix()} md5={rom_md5}",
        "return {",
    ]
    for target in targets:
        index = int(target["pointer_index"])
        cpu = int(target["cpu_address"])
        record_offset = int(target["record_rom_offset"])
        end_cpu = int(target["record_end_cpu"])
        prg_bank = int(target["prg_bank"])
        payload = target["bytes"]
        assert isinstance(payload, bytes)
        hex_bytes = payload.hex(" ").upper()
        lines.append(
            "  { "
            f"label = \"manifest_ptr_{index:03d}_candidate\", "
            "category = \"pointer_dialogue\", "
            f"rom = 0x{record_offset:05X}, prg_bank = {prg_bank}, start = 0x{cpu:04X}, stop = 0x{end_cpu:04X}, "
            f"bytes = \"{hex_bytes}\", old_bytes = \"{hex_bytes}\", "
            f"source = \"Generated from candidate pointer {index}\", "
            "korean = \"Candidate runtime target; native visual gate remains UNKNOWN\" },"
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--pointer-index", type=int, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-length", type=lambda value: int(value, 0), default=0x200)
    args = parser.parse_args()

    candidate = args.candidate.expanduser().resolve()
    if not candidate.is_file():
        raise SystemExit(f"candidate ROM not found: {candidate}")
    rom = candidate.read_bytes()
    if len(rom) < POINTER_TABLE_OFFSET + POINTER_COUNT * 2:
        raise SystemExit("candidate ROM is too small for the declared pointer table")
    if args.max_length <= 0:
        raise SystemExit("--max-length must be positive")
    targets = [read_target(rom, index, args.max_length) for index in args.pointer_index]
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.md5(rom).hexdigest()
    output.write_text(render_lua(candidate, digest, targets), encoding="utf-8")
    for target in targets:
        print(
            f"pointer={target['pointer_index']} "
            f"cpu=0x{int(target['cpu_address']):04X} "
            f"rom=0x{int(target['record_rom_offset']):05X} "
            f"prg_bank={int(target['prg_bank'])} "
            f"length={len(target['bytes'])}"
        )
    print(f"candidate_md5={digest}")
    print(f"target={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

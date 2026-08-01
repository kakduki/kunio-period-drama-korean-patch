#!/usr/bin/env python3
"""Find likely 6502 absolute references to RAM addresses in the PRG image."""

from __future__ import annotations

import argparse
from pathlib import Path


OP_NAMES = {
    0x0D: "ORA abs",
    0x1D: "ORA abs,X",
    0x19: "ORA abs,Y",
    0x2D: "AND abs",
    0x3D: "AND abs,X",
    0x39: "AND abs,Y",
    0x4D: "EOR abs",
    0x5D: "EOR abs,X",
    0x59: "EOR abs,Y",
    0x6D: "ADC abs",
    0x7D: "ADC abs,X",
    0x79: "ADC abs,Y",
    0x8D: "STA abs",
    0x9D: "STA abs,X",
    0x99: "STA abs,Y",
    0xAC: "LDY abs",
    0xBC: "LDY abs,X",
    0xAD: "LDA abs",
    0xBD: "LDA abs,X",
    0xB9: "LDA abs,Y",
    0xCC: "CPY abs",
    0xCD: "CMP abs",
    0xDD: "CMP abs,X",
    0xD9: "CMP abs,Y",
    0xEC: "CPX abs",
    0xED: "SBC abs",
    0xFD: "SBC abs,X",
    0xF9: "SBC abs,Y",
    0xCE: "DEC abs",
    0xEE: "INC abs",
}


def parse_hex_list(value: str) -> list[int]:
    result = []
    for item in value.split(","):
        item = item.strip()
        if item:
            result.append(int(item, 0))
    return result


def cpu_hint(prg_offset: int, prg_bank_size: int = 0x2000) -> str:
    bank = prg_offset // prg_bank_size
    in_bank = prg_offset % prg_bank_size
    if bank >= 14:
        return f"bank={bank:02X} cpu=${0xC000 + (bank - 14) * 0x2000 + in_bank:04X} (fixed/possible)"
    windows = [0x8000, 0xA000, 0xC000]
    return f"bank={bank:02X} cpu=" + "/".join(f"${base + in_bank:04X}" for base in windows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument(
        "--targets",
        default="0x04F1,0x04FA,0x04FB,0x04FC,0x04FD,0x0732,0x0733,0x0734,0x0735,0x07A8,0x07A9,0x07BB,0x07C3,0x07C5,0x07C9",
    )
    args = parser.parse_args()

    data = args.rom.read_bytes()
    if data[:4] != b"NES\x1a":
        raise SystemExit(f"not an iNES ROM: {args.rom}")
    prg_size = data[4] * 0x4000
    prg = data[16 : 16 + prg_size]
    targets = set(parse_hex_list(args.targets))
    hits: dict[int, list[str]] = {target: [] for target in sorted(targets)}

    for offset in range(0, max(0, len(prg) - 2)):
        opcode = prg[offset]
        if opcode not in OP_NAMES:
            continue
        target = prg[offset + 1] | (prg[offset + 2] << 8)
        if target not in hits:
            continue
        hits[target].append(
            f"{offset:06X} {cpu_hint(offset)} {OP_NAMES[opcode]} ${target:04X}"
        )

    print(f"ROM={args.rom}")
    print(f"PRG_BYTES={len(prg)} PRG_BANKS_8K={len(prg) // 0x2000}")
    for target in sorted(targets):
        print(f"\nTARGET ${target:04X} HITS={len(hits[target])}")
        for hit in hits[target][:80]:
            print(hit)
        if len(hits[target]) > 80:
            print(f"... {len(hits[target]) - 80} more")


if __name__ == "__main__":
    main()

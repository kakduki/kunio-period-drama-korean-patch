#!/usr/bin/env python3
"""Find static references to PPU registers in PRG ROM."""
from collections import defaultdict

from rom_utils import find_rom_path


PPU_REGS = {
    0x2000: "PPUCTRL",
    0x2001: "PPUMASK",
    0x2002: "PPUSTATUS",
    0x2005: "PPUSCROLL",
    0x2006: "PPUADDR",
    0x2007: "PPUDATA",
}

OPCODES = {
    0x8D: ("STA", "abs", 3),
    0x9D: ("STA", "abs,X", 3),
    0x99: ("STA", "abs,Y", 3),
    0xAD: ("LDA", "abs", 3),
    0xBD: ("LDA", "abs,X", 3),
    0xB9: ("LDA", "abs,Y", 3),
    0x2C: ("BIT", "abs", 3),
    0xEE: ("INC", "abs", 3),
    0xCE: ("DEC", "abs", 3),
}


def cpu_addr_for_bank_offset(bank: int, bank_offset: int) -> int:
    # MMC3 can swap 8KB windows, but this static view is still useful for
    # correlating trace logs with PRG offsets.
    return 0x8000 + bank_offset


with open(find_rom_path(), "rb") as f:
    data = f.read()

prg = data[16:16 + 131072]
hits_by_reg = defaultdict(list)

for offset in range(len(prg) - 2):
    op = prg[offset]
    if op not in OPCODES:
        continue

    addr = prg[offset + 1] | (prg[offset + 2] << 8)
    if addr not in PPU_REGS:
        continue

    bank = offset // 0x4000
    bank_offset = offset % 0x4000
    mnemonic, mode, _ = OPCODES[op]
    hits_by_reg[addr].append((bank, bank_offset, offset + 16, mnemonic, mode))

print("=== Static PPU register references ===")
for addr, name in PPU_REGS.items():
    hits = hits_by_reg.get(addr, [])
    print(f"\n${addr:04X} {name}: {len(hits)} references")
    for bank, bank_offset, rom_offset, mnemonic, mode in hits[:80]:
        cpu_addr = cpu_addr_for_bank_offset(bank, bank_offset)
        print(
            f"  ROM+0x{rom_offset:05X} bank {bank} "
            f"bank+0x{bank_offset:04X} CPU~${cpu_addr:04X}: "
            f"{mnemonic} ${addr:04X} ({mode})"
        )

print("\nNotes:")
print("- $2006/$2007 writes are the main targets for nametable/text output tracing.")
print("- MMC3 bank switching means CPU~ addresses are approximate static views.")

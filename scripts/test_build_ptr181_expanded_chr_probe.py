#!/usr/bin/env python3

from build_opening_dialogue_16x16_proof import default_square_font
from build_ptr181_bank8_page_probe import CHR_BANK_SIZE, resolve_base_rom
from build_ptr181_expanded_chr_probe import (
    EXPANDED_CHR_BANKS,
    EXPANDED_R1,
    MAPPER_SELECT_CAVE_ROM_OFFSET,
    patch_expanded_chr,
)


def main() -> int:
    base = resolve_base_rom(None).read_bytes()
    patched = patch_expanded_chr(base, default_square_font(None))
    assert len(patched) == len(base) + CHR_BANK_SIZE
    assert patched[5] == EXPANDED_CHR_BANKS
    assert patched[0x20010:len(base)] == base[0x20010:]
    select = patched[MAPPER_SELECT_CAVE_ROM_OFFSET:MAPPER_SELECT_CAVE_ROM_OFFSET + 28]
    assert bytes.fromhex("A9 3C 8D 02 05 A9") + bytes((EXPANDED_R1,)) in select
    assert patched[len(base):] != b"\x00" * CHR_BANK_SIZE
    print("PTR-181 expanded CHR probe tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from build_opening_dialogue_16x16_proof import default_square_font
from build_opening_dialogue_8x16_proof import CODE_CAVE_ROM_OFFSET, CODE_CAVE_SIZE
from build_ptr181_bank8_page_probe import RECORD_ROM_OFFSET, resolve_base_rom
from build_ptr181_expanded_code_pool_probe import (
    HELPER_NEW_END,
    PROBE_GLYPH_PAIRS,
    PROBE_RECORD,
    patch_code_pool,
)


def main() -> int:
    base = resolve_base_rom(None).read_bytes()
    patched = patch_code_pool(base, default_square_font(None))
    helper = patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE]
    assert helper.count(HELPER_NEW_END) == 2
    assert patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + len(PROBE_RECORD)] == PROBE_RECORD
    source_codes = [code for pair in PROBE_GLYPH_PAIRS.values() for code in pair]
    assert 0x8A in source_codes and 0x8B in source_codes
    assert min(source_codes) == 0x81 and max(source_codes) == 0xDF
    assert 0xCA not in source_codes
    print("PTR-181 expanded code-pool probe tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

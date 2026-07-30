#!/usr/bin/env python3

from build_opening_dialogue_8x16_proof import default_tall_font
from build_ptr181_bank8_page_probe import RECORD_ROM_OFFSET, resolve_base_rom
from build_ptr181_korean_8x16_candidate import (
    GLYPH_CODES,
    KOREAN_RECORD,
    patch_korean_8x16,
)


def main() -> int:
    base = resolve_base_rom(None).read_bytes()
    patched = patch_korean_8x16(base, default_tall_font(None))
    assert patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + len(KOREAN_RECORD)] == KOREAN_RECORD
    assert len(GLYPH_CODES) == 7
    assert patched[5] == 17
    print("PTR-181 Korean 8x16 candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

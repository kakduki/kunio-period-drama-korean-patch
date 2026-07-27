#!/usr/bin/env python3
"""Test the isolated Bank 8 tier-2 builder contract."""

from build_opening_dialogue_bank8_static_r1_safe_capacity_tier2 import (
    MAPPER_SETUP_ORIGINAL,
    R1_WINDOW_BASE_CODE,
    R1_WINDOW_SIZE,
    SOURCE_CHR_BANK,
    STATIC_R1,
    TARGET_CHR_BANK,
)


def main() -> int:
    assert MAPPER_SETUP_ORIGINAL == bytes.fromhex("A9 3C 8D 02 05 A9 3E 8D 03 05")
    assert SOURCE_CHR_BANK == 7
    assert TARGET_CHR_BANK == 8
    assert R1_WINDOW_BASE_CODE == 0x80
    assert R1_WINDOW_SIZE == 0x800
    assert STATIC_R1 == 0x46
    print("Safe static-R1 tier-2 capacity builder tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

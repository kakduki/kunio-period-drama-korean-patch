#!/usr/bin/env python3
"""Test the static R1 tier-2 capacity builder imports and constants."""

from build_opening_dialogue_bank8_static_r1_capacity_tier2 import (
    MAPPER_SETUP_ORIGINAL,
    STATIC_R1,
    TARGET_CHR_BANK,
)


def main() -> int:
    assert MAPPER_SETUP_ORIGINAL == bytes.fromhex("A9 3C 8D 02 05 A9 3E 8D 03 05")
    assert STATIC_R1 == 0x46
    assert TARGET_CHR_BANK == 8
    print("Static-R1 tier-2 capacity builder tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

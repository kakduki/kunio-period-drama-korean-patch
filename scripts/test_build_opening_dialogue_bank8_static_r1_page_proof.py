#!/usr/bin/env python3
"""Test the normal mapper static-R1 proof builder."""

from build_opening_dialogue_bank8_static_r1_page_proof import (
    MAPPER_SETUP_ORIGINAL,
    SOURCE_PAGE_SEQUENCE,
    STATIC_R1,
)


def main() -> int:
    assert MAPPER_SETUP_ORIGINAL == bytes.fromhex("A9 3C 8D 02 05 A9 3E 8D 03 05")
    assert SOURCE_PAGE_SEQUENCE == bytes.fromhex("A9 40 8D 02 05 A9 42 8D 03 05")
    assert STATIC_R1 == 0x46
    print("Static-R1 page proof builder tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

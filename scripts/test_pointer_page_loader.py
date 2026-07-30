#!/usr/bin/env python3
"""Test the common dialogue pointer-to-CHR-page loader."""

from __future__ import annotations

from pointer_page_loader import (
    HIGH_TABLE_CONTINUE_CPU,
    LOADER_CAVE_SIZE,
    LOADER_HOOK_CPU,
    LOW_TABLE_CONTINUE_CPU,
    PAGE_TABLE_CPU,
    RENDER_SOURCE_RANGES,
    build_generic_mapper_helpers,
    build_loader_helper,
    build_page_scoped_renderer,
    encode_page_table,
    loader_hook,
    mapper_page_value,
)


def main() -> int:
    assignments: list[int | None] = [None] * 248
    assignments[0] = 0
    assignments[181] = 43
    assignments[247] = 63
    table = encode_page_table(assignments)
    assert len(table) == 248
    assert table[0] == 1
    assert table[181] == 44
    assert table[247] == 64

    helper = build_loader_helper()
    assert len(helper) <= LOADER_CAVE_SIZE
    assert bytes((0xBD, PAGE_TABLE_CPU & 0xFF, PAGE_TABLE_CPU >> 8)) in helper
    assert helper.endswith(
        bytes(
            (
                0x4C, LOW_TABLE_CONTINUE_CPU & 0xFF, LOW_TABLE_CONTINUE_CPU >> 8,
                0x4C, HIGH_TABLE_CONTINUE_CPU & 0xFF, HIGH_TABLE_CONTINUE_CPU >> 8,
            )
        )
    )
    hook = loader_hook()
    assert hook == bytes((0x4C, 0xF0, 0xAF, 0xEA, 0xEA))
    assert LOADER_HOOK_CPU == 0x9137
    assert mapper_page_value(1) == 0x80
    assert mapper_page_value(4) == 0x86
    assert mapper_page_value(64) == 0xFE
    renderer, marker_cpu = build_page_scoped_renderer(0xBFB4, 92)
    assert len(renderer) <= 92
    assert marker_cpu > 0xBFB4
    assert bytes.fromhex("AD FF 07") in renderer
    assert RENDER_SOURCE_RANGES == ((0x81, 0x9B), (0xC0, 0xC8))

    original_wrapper = bytes(range(30))
    wrapper, select, store = build_generic_mapper_helpers(original_wrapper)
    assert len(wrapper) == len(original_wrapper)
    assert wrapper[8:11] == bytes.fromhex("20 B1 F2")
    assert bytes.fromhex("AD FF 07 38 E9 01 0A 09 80") in select
    assert store.endswith(bytes.fromhex("8D 03 05 60"))

    for invalid in (-1, 64):
        bad = list(assignments)
        bad[3] = invalid
        try:
            encode_page_table(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid page assignment was accepted")

    print("Pointer page loader tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

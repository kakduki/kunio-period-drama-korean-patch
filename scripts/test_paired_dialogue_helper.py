#!/usr/bin/env python3
"""Focused invariants for record-scoped paired 16x16 renderer helpers."""

from __future__ import annotations

from paired_dialogue_helper import HelperAssemblyError, build_record_scoped_paired_helper


def main() -> int:
    helper = build_record_scoped_paired_helper(
        record_cpu_addresses=(0xB1A6, 0xB1C7),
        source_ranges=((0x81, 0x9F), (0xC0, 0xC8)),
        entry_cpu=0xBFA5,
        max_size=0x5B,
    )
    assert helper.entry_cpu == 0xBFA5
    assert helper.marker_cpu == helper.entry_cpu + helper.entry_length
    assert len(helper.code) <= 0x5B
    assert helper.marker_hook == bytes((0x4C, helper.marker_cpu & 0xFF, helper.marker_cpu >> 8))
    for code in (0x81, 0x9E, 0xC0, 0xC7):
        assert helper.accepts_source_code(code)
    for code in (0x80, 0x9F, 0xBB, 0xCA, 0xC8):
        assert not helper.accepts_source_code(code)

    try:
        build_record_scoped_paired_helper(
            record_cpu_addresses=(0xB1A6, 0xB2C7),
            source_ranges=((0x81, 0x9F),),
            entry_cpu=0xBFA5,
            max_size=0x5B,
        )
    except HelperAssemblyError:
        pass
    else:
        raise AssertionError("mixed-bank record guard must be rejected")

    print("Record-scoped paired dialogue helper tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

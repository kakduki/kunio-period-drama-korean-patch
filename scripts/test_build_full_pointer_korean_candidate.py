#!/usr/bin/env python3
"""Test full control-preserving pointer-dialogue compilation."""

from __future__ import annotations

import hashlib

from build_full_pointer_korean_candidate import (
    PAGE_COUNT,
    POINTER_COUNT,
    SOURCE_CODES,
    apply_full_candidate,
    build_config,
    control_skeleton,
    encode_control_preserving_record,
)
from build_opening_dialogue_8x16_proof import default_tall_font
from build_ptr181_bank8_page_probe import resolve_base_rom
from pointer_page_loader import PAGE_TABLE_ROM_OFFSET


def main() -> int:
    glyph_codes = {"가": 0x81, "나": 0x82, "다": 0x83}
    template = bytes.fromhex("94 93 95 95 BB 00 82 92 8F 94 88 85 92 CA 00 97 81 89 94 CA FF")
    encoded = encode_control_preserving_record(template, "가 나 다", glyph_codes)
    assert control_skeleton(encoded, korean_codes=True) == control_skeleton(template)
    assert bytes((0xBB,)) in encoded and encoded.endswith(bytes.fromhex("CA FF"))

    base = resolve_base_rom(None).read_bytes()
    config = build_config(base)
    assert len(config["records"]) == POINTER_COUNT
    assert len(config["pages"]) == PAGE_COUNT
    assert len(SOURCE_CODES) == 34
    assert config["record_end"] <= 0x07000
    assert config["record_loader_gap"] >= 0
    assert all(
        control_skeleton(record["record"], korean_codes=True)
        == bytes.fromhex(record["english_control_skeleton"])
        for record in config["records"]
        if record["record"] and not record["excluded"]
    )

    patched, targets = apply_full_candidate(base, config, default_tall_font(None))
    assert patched[5] == 29
    assert len(patched) == len(base) + 13 * 0x2000
    assert hashlib.md5(patched).hexdigest() == "1e51b3bebb4a5d1b97d2001c84a73204"
    table = patched[PAGE_TABLE_ROM_OFFSET:PAGE_TABLE_ROM_OFFSET + POINTER_COUNT]
    assert sum(value != 0 for value in table) == 244
    assert max(table) == PAGE_COUNT
    assert any(target["kind"] == "full_dialogue_records" for target in targets)
    print("Full pointer Korean candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

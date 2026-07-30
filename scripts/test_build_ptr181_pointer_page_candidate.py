#!/usr/bin/env python3
"""Test the PTR-181 common pointer-page development candidate."""

from __future__ import annotations

from build_opening_dialogue_8x16_proof import default_tall_font
from build_ptr181_bank8_page_probe import resolve_base_rom
from build_ptr181_pointer_page_candidate import apply_pointer_page_candidate
from pointer_page_loader import (
    LOADER_CAVE_ROM_OFFSET,
    LOADER_HOOK_ROM_OFFSET,
    PAGE_TABLE_ROM_OFFSET,
    build_loader_helper,
    loader_hook,
)


def main() -> int:
    base = resolve_base_rom(None).read_bytes()
    patched, targets = apply_pointer_page_candidate(base, default_tall_font(None))
    assert patched[LOADER_HOOK_ROM_OFFSET:LOADER_HOOK_ROM_OFFSET + 5] == loader_hook()
    loader = build_loader_helper()
    assert patched[LOADER_CAVE_ROM_OFFSET:LOADER_CAVE_ROM_OFFSET + len(loader)] == loader
    table = patched[PAGE_TABLE_ROM_OFFSET:PAGE_TABLE_ROM_OFFSET + 248]
    assert table[181] == 4
    assert sum(value != 0 for value in table) == 1
    assert patched[5] == 17
    assert any(target["kind"] == "pointer_page_table" for target in targets)
    print("PTR-181 pointer-page candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from pathlib import Path

from build_ptr181_conditional_mapper_probe import (
    MAPPER_SELECT_CAVE_ROM_OFFSET,
    MAPPER_STORE_CAVE_ROM_OFFSET,
    MAPPER_WRAPPER_ROM_OFFSET,
    mapper_helpers,
    flagged_renderer_helper,
    patch_candidate,
)
from build_ptr181_bank8_page_probe import resolve_base_rom
from build_opening_dialogue_16x16_proof import default_square_font


def main() -> int:
    base = resolve_base_rom(None).read_bytes()
    wrapper, select, store = mapper_helpers()
    assert wrapper[8:11] == bytes.fromhex("20 B1 F2")
    assert select[-6:] == bytes.fromhex("4C FD F2 4C EE F2")
    assert store == bytes.fromhex(
        "A9 00 8D FF 07 A9 3C 8D 02 05 A9 3E EA EA EA 8D 03 05 60"
    )
    renderer, marker_cpu = flagged_renderer_helper()
    assert bytes.fromhex("A9 01 8D FF 07") in renderer
    assert marker_cpu == 0xBFD8
    patched, targets = patch_candidate(base, default_square_font(None))
    assert patched[MAPPER_WRAPPER_ROM_OFFSET:MAPPER_WRAPPER_ROM_OFFSET + len(wrapper)] == wrapper
    assert patched[MAPPER_SELECT_CAVE_ROM_OFFSET:MAPPER_SELECT_CAVE_ROM_OFFSET + len(select)] == select
    assert patched[MAPPER_STORE_CAVE_ROM_OFFSET:MAPPER_STORE_CAVE_ROM_OFFSET + len(store)] == store
    assert any(target["kind"] == "conditional_mapper_wrapper" for target in targets)
    print("PTR-181 conditional mapper probe tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

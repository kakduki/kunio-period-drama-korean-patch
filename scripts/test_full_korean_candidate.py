#!/usr/bin/env python3
"""Check the generated full candidate and its composed patch contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_main_menu_korean_candidate import TEMPLATE_LENGTH, TEMPLATE_ROM_OFFSET
from build_opening_dialogue_proof import resolve_base_rom
from build_patch import make_records
from pointer_page_loader import build_loader_helper_with_direct_mapper, build_page_scoped_renderer
from rom_utils import REPO_ROOT


def main() -> int:
    base_path = resolve_base_rom(None)
    base = base_path.read_bytes()
    candidate_path = REPO_ROOT / "output" / "full_korean_candidate" / "kunio_period_drama_korean_full_candidate.nes"
    ips_path = REPO_ROOT / "output" / "full_korean_candidate" / "kunio_period_drama_korean_full_candidate.ips"
    candidate = candidate_path.read_bytes()

    assert hashlib.md5(base).hexdigest() == "0d406a85285b4de8468f0dab6aad5fe5"
    assert candidate[5] == 29
    assert apply_ips(base, ips_path) == candidate
    assert len(make_records(base, candidate)) == 193
    assert candidate[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH] != base[
        TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH
    ]
    assert candidate[0x1EE5D] == 0x3E, "source-page menu candidate must not globally change R1"
    loader = build_loader_helper_with_direct_mapper(0xB030)
    assert len(loader) == 64
    assert bytes((0xA8, 0x88)) in loader, 'loader must preserve X by indexing the page table through Y'
    renderer, _marker = build_page_scoped_renderer(0xBFA5, 0x5B, map_r1_from_page_state=True)
    assert len(renderer) == 90

    smoke = json.loads(
        (REPO_ROOT / "rom_analysis" / "full_korean_candidate_smoke_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert smoke["status"] == "SOFT_GATE_PASS_MENU_AND_GAMEPLAY_ENTRY"
    assert all(smoke["checks"].values())
    print(f"candidate_md5={hashlib.md5(candidate).hexdigest()}")
    print("Full Korean candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Focused invariants for the combined opening/menu development build."""

from __future__ import annotations

from build_korean_development_candidate import build_candidate
from build_opening_dialogue_proof import resolve_base_rom
from build_main_menu_korean_candidate import default_square_font


def main() -> int:
    base_path = resolve_base_rom(None)
    base = base_path.read_bytes()
    opening = bytearray(base)
    opening[0x071B6] ^= 0x01
    patched, targets, details = build_candidate(
        base,
        bytes(opening),
        font_path=default_square_font(None),
    )
    assert patched != base
    assert patched != bytes(opening)
    assert targets
    assert details["opening_change_count"] == 1
    assert details["menu_change_count"] > 0
    assert details["total_change_count"] > details["menu_change_count"]
    print("Combined Korean development candidate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

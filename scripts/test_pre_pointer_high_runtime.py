#!/usr/bin/env python3
"""Check the bounded high-code candidate evidence without shipping a ROM."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


REPORT = REPO_ROOT / "rom_analysis" / "pre_pointer_high_runtime.json"


def main() -> int:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    assert payload["release_status"] == "NOT_READY"
    assert payload["source_contract"]["prg_bank"] == 1
    assert payload["source_contract"]["top_tile_base"] == "$181"
    assert payload["english_probe"]["lua_done"] is True
    assert payload["english_probe"]["matched_rows"] == 10
    assert payload["korean_probe"]["lua_done"] is True
    assert payload["korean_probe"]["matched_rows"] == 9
    assert payload["korean_probe"]["missing_rows"] == ["EN-PRE-138"]
    assert payload["main_menu_context"]["english"]["ppu_read_ok"] is True
    assert payload["main_menu_context"]["korean"]["ppu_read_ok"] is True
    print("PASS pre-pointer high-code runtime evidence report")
    print("english_exact_owner=10/10")
    print("korean_exact_owner=9/10")
    print("release_status=NOT_READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

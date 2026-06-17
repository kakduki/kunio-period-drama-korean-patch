#!/usr/bin/env python3
"""Check the generated primary visual checklist."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


JSON_PATH = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
MD_PATH = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.md"


def main() -> int:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    summary = payload["summary"]
    rows = payload["rows"]

    assert summary["row_count"] == 10
    assert summary["primary_rom"] == "output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes"
    assert summary["watcher_lua"] == "lua/kunio_manual_v042_capture_watch.lua"
    assert rows[0]["rom_hit"] == "0x07227"
    assert rows[0]["evidence_level"] == "runtime-confirmed"
    assert any(row["romaji"] == "Heishichi" for row in rows)
    assert summary["status_counts"].get("not_in_manual_capture_cards", 0) >= 1

    md = MD_PATH.read_text(encoding="utf-8")
    assert "Primary Visual Checklist" in md
    assert "lua/kunio_manual_v042_capture_watch.lua" in md
    assert "0x07227" in md

    print("OK: primary visual checklist prioritizes current v0.4.2 rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

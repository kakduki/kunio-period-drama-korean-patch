#!/usr/bin/env python3
"""Check the generated font expansion readiness gate."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


JSON_PATH = REPO_ROOT / "rom_analysis" / "font_expansion_readiness.json"
MD_PATH = REPO_ROOT / "rom_analysis" / "font_expansion_readiness.md"
BATCH46_REPORT = REPO_ROOT / "rom_analysis" / "kunio_period_drama_korean_font_expansion_v0.5_batch46_report.json"


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    summary = data["summary"]
    batches = {batch["requested_extra_glyphs"]: batch for batch in data["batches"]}

    assert summary["font_bin_matches_char_map"] is True
    assert summary["max_prefix_buildable_extra_glyphs"] == 46

    assert batches[32]["buildable_with_current_font_assets"] is True
    assert batches[32]["missing_glyph_count"] == 0

    batch64 = batches[64]
    assert batch64["buildable_with_current_font_assets"] is False
    assert batch64["first_missing_glyph"] == "\uc7ac"
    assert batch64["first_missing_slot"] == "0x141"

    batch46 = json.loads(BATCH46_REPORT.read_text(encoding="utf-8"))
    assert batch46["candidate"] == "v0.5 font-expansion batch 46"
    assert batch46["added_glyph_count"] == summary["max_prefix_buildable_extra_glyphs"]
    assert batch46["glyphs_written"] == 64
    assert batch46["escaped_chr_bank7_bytes"] == 0
    assert batch46["patched_md5"] == "5e10cabaff7452fe842726194f4ac843"

    md = MD_PATH.read_text(encoding="utf-8")
    assert "Font Expansion Readiness" in md
    assert "max prefix buildable extra glyphs" in md
    assert "First Blocked Batch: 64 Extra Glyphs" in md

    print("OK: font expansion readiness gate matches current font assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check the generated batch46 text-readiness report."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


JSON_PATH = REPO_ROOT / "rom_analysis" / "batch46_text_readiness.json"
MD_PATH = REPO_ROOT / "rom_analysis" / "batch46_text_readiness.md"


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    summary = data["summary"]

    assert summary["queued_hits"] == 60
    assert summary["batch46_added_glyphs"] == 46
    assert summary["v042_font_ready"] == 27
    assert summary["batch46_font_ready"] == 27
    assert summary["newly_font_ready_after_batch46"] == 0
    assert summary["screen_proof_candidates_after_batch46"] == 7
    assert summary["new_screen_proof_candidates_after_batch46"] == 0

    candidates = data["screen_proof_candidates"]
    assert len(candidates) == 7
    assert {row["rom_offset"] for row in candidates} == {
        "0x0440C",
        "0x048F4",
        "0x052A5",
        "0x05BE5",
        "0x06294",
        "0x0631B",
        "0x06359",
    }
    assert all(row["promotable_after_batch46_screen_proof"] for row in candidates)

    md = MD_PATH.read_text(encoding="utf-8")
    assert "Batch46 Text Readiness" in md
    assert "Newly font-ready after batch46: **0**" in md
    assert "Screen-proof candidates after batch46: **7**" in md

    print("OK: batch46 text readiness matches the current broad-scan gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

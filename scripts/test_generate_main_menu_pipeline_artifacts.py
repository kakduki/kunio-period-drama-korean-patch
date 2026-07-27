#!/usr/bin/env python3
"""Focused output coverage for the main-menu pipeline artifact generator."""

from __future__ import annotations

import tempfile
from pathlib import Path

from generate_main_menu_pipeline_artifacts import write_artifacts


def main() -> int:
    context = {
        "overall_verdict": "PASS",
        "source": {"template_rom_offset": "0x1F2C1"},
        "labels": [
            {
                "id": "items",
                "rom_offset": "0x1F2E3",
                "base_bytes": "A3 91",
                "english_reference": "ITEMS",
                "korean_candidate": "\ubb3c\uac74",
            }
        ],
    }
    candidate = {
        "source": {
            "base_md5": "base",
            "template_rom_offset": "0x1F2C1",
            "raster_r1_original": "0x3E",
            "raster_r1_clone": "0x46",
            "raster_r1_cpu_address": "0xEE4D",
            "source_chr_1k_pair": "0x3E",
            "clone_chr_1k_pair": "0x46",
        },
        "candidate": {"patched_md5": "candidate", "changed_span_count": 3},
    }
    smoke = {
        "status": "SOFT_GATE_PASS",
        "release_verdict": "UNKNOWN",
        "checks": {
            "captured_template_matches_candidate": True,
            "lua_done": True,
            "final_mapper_r1_is_clone": True,
            "source_bank7_chr_pair_unchanged": True,
        },
        "capture": {
            "screen": "screen.png",
            "final_mapper_snapshot": {"r1": "46"},
        },
    }
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        paths = write_artifacts(root, context, candidate, smoke)
        assert len(paths) == 8
        assert (root / "build_matrix.md").is_file()
        strings = (root / "string_candidates.csv").read_text(encoding="utf-8")
        assert "PTR-182-OPENING-COMPACT-16X16" in strings
        assert "MENU-ITEMS" in strings
        assert "SOFT_GATE_PASS" in (root / "patched_rom_report.md").read_text(encoding="utf-8")
        assert "UNKNOWN" in (root / "release_gate_checklist.md").read_text(encoding="utf-8")
        assert (root / "rom_analysis" / "main_menu_cursor_probe.md").is_file()
    print("Main-menu pipeline artifact generator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

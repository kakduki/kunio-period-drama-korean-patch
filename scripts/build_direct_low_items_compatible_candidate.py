#!/usr/bin/env python3
"""Build direct-low UI with the Items title glyph slots reserved.

This is the composition-safe variant of the direct-low candidate.  Items
title/NONE uses low codes 0x20-0x27 on the fixed Bank 7 R0 page, so those codes
must remain available for the later Items owner-chain stage.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_direct_low_korean_candidate import build
from rom_utils import REPO_ROOT


DEFAULT_INPUT = REPO_ROOT / "output" / "full_korean_candidate" / "kunio_period_drama_korean_full_candidate.nes"
DEFAULT_BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
DEFAULT_REFERENCE_IPS = REPO_ROOT / "tools" / "reference" / "TSe-v10.ips"
DEFAULT_REFERENCE_MAP = REPO_ROOT / "rom_analysis" / "english_patch_reference.json"
DEFAULT_LABELS = REPO_ROOT / "text_data" / "direct_low_korean_labels.json"
DEFAULT_CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
DEFAULT_FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_direct_low_items_compatible_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_direct_low_items_compatible_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_direct_low_items_compatible_candidate.md"

# Items title/NONE owns 0x20-0x27 and uses 0x38 as a trailing blank.
RESERVED_LOW_CODES = set(range(0x20, 0x28)) | {0x38}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-rom", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--reference-ips", type=Path, default=DEFAULT_REFERENCE_IPS)
    parser.add_argument("--reference-map", type=Path, default=DEFAULT_REFERENCE_MAP)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--font-bin", type=Path, default=DEFAULT_FONT_BIN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()
    payload = build(
        args.input_rom.resolve(),
        args.base_rom.resolve(),
        args.reference_ips.resolve(),
        args.reference_map.resolve(),
        args.labels.resolve(),
        args.char_map.resolve(),
        args.font_bin.resolve(),
        args.out_dir.resolve(),
        args.report_json.resolve(),
        args.report_markdown.resolve(),
        RESERVED_LOW_CODES,
    )
    payload["composition"] = {
        "reserved_low_codes": [f"0x{code:02X}" for code in sorted(RESERVED_LOW_CODES)],
        "reserved_owner": "Items title/NONE",
        "direct_low_owner": "all other direct-low labels",
    }
    args.report_json.resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

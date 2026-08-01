#!/usr/bin/env python3
"""Build the 22-row integrated fixed-label expansion candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_pre_pointer_high_candidate import (
    DEFAULT_BASE,
    DEFAULT_CHAR_MAP,
    default_tall_font,
    DEFAULT_INVENTORY,
    DEFAULT_REFERENCE_IPS,
    build,
)
from generate_pre_pointer_korean_probe import DEFAULT_TEMPLATE, generate
from rom_utils import REPO_ROOT


DEFAULT_INPUT = (
    REPO_ROOT
    / "output"
    / "full_pointer_korean_candidate"
    / "kunio_period_drama_korean_full_pointer_candidate.nes"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_expanded_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_expanded_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_expanded_candidate.md"
DEFAULT_PROBE = REPO_ROOT / "lua" / "kunio_pre_pointer_expanded_korean_probe.lua"
OUT_STEM = "kunio_period_drama_korean_expanded_candidate"

TARGET_OFFSETS = {
    0x05AEB,
    0x05B1B,
    0x05B24,
    0x05B4E,
    0x05B61,
    0x05B69,
    0x05B85,
    0x05B8B,
    0x05BA2,
    0x05CE0,
    0x05AAD,
    0x05AB3,
    0x05AC2,
    0x05ACB,
    0x05AE2,
    0x05B0B,
    0x05B13,
    0x05B3D,
    0x05B44,
    0x05B49,
    0x05B6F,
    0x05B7F,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-rom", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-rom", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--reference-ips", type=Path, default=DEFAULT_REFERENCE_IPS)
    parser.add_argument("--char-map", type=Path, default=DEFAULT_CHAR_MAP)
    parser.add_argument("--font", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--probe", type=Path, default=DEFAULT_PROBE)
    args = parser.parse_args()

    payload = build(
        args.input_rom.resolve(),
        args.base_rom.resolve(),
        args.inventory.resolve(),
        args.reference_ips.resolve(),
        args.char_map.resolve(),
        args.font.resolve() if args.font else default_tall_font(None),
        args.out_dir.resolve(),
        args.report_json.resolve(),
        args.report_markdown.resolve(),
        OUT_STEM,
        target_offsets=TARGET_OFFSETS,
        allow_missing_glyphs=True,
    )
    generated = generate(args.report_json.resolve(), DEFAULT_TEMPLATE, args.probe.resolve())
    payload["generated_probe_targets"] = generated
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

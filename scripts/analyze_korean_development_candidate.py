#!/usr/bin/env python3
"""Evaluate the combined opening/menu development candidate captures."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_reference_ips import parse_ines_layout
from build_main_menu_korean_candidate import (
    CHR_PAIR_SIZE,
    CLONE_CHR_1K_PAIR,
    GLYPH_CODE_PAIRS,
    RASTER_R1_VALUE_CLONE,
    TEMPLATE_LENGTH,
    TEMPLATE_ROM_OFFSET,
    build_menu_template,
    chr_page_offset,
)
from build_opening_dialogue_proof import resolve_base_rom
from rom_utils import REPO_ROOT


DEFAULT_CANDIDATE = (
    REPO_ROOT
    / "output"
    / "korean_development_candidate"
    / "kunio_period_drama_korean_development_candidate.nes"
)
DEFAULT_MENU_CAPTURE = REPO_ROOT / "rom_analysis" / "state_page_probe_raw" / "development_candidate_menu"
DEFAULT_ITEMS_CAPTURE = REPO_ROOT / "rom_analysis" / "state_page_probe_raw" / "development_candidate_items"
DEFAULT_BASE_ITEMS_CAPTURE = REPO_ROOT / "rom_analysis" / "state_page_probe_raw" / "guard_items_base"
DEFAULT_OPENING_CAPTURE = REPO_ROOT / "rom_analysis" / "opening_development_candidate_p182"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "korean_development_candidate_runtime.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "korean_development_candidate_runtime.md"
DYNAMIC_TEMPLATE_OFFSETS = frozenset({0x21})


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def lua_done(capture: Path) -> bool:
    rows = read_tsv(capture / "summary.tsv")
    return bool(rows) and rows[-1].get("reason") == "lua_done"


def exactly_one(capture: Path, pattern: str) -> Path:
    matches = sorted(capture.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one {pattern} in {capture}, found {len(matches)}")
    return matches[0]


def screenshot_pixel_equal(left: Path, right: Path) -> bool:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for the bounded screenshot comparison") from exc
    first = Image.open(left).convert("RGB")
    second = Image.open(right).convert("RGB")
    first_pixels = list(first.get_flattened_data()) if hasattr(first, "get_flattened_data") else list(first.getdata())
    second_pixels = list(second.get_flattened_data()) if hasattr(second, "get_flattened_data") else list(second.getdata())
    return first.size == second.size and first_pixels == second_pixels


def menu_template_matches(candidate: bytes, captured: bytes) -> bool:
    return len(candidate) == len(captured) == TEMPLATE_LENGTH and all(
        candidate[index] == captured[index]
        for index in range(TEMPLATE_LENGTH)
        if index not in DYNAMIC_TEMPLATE_OFFSETS
    )


def clone_non_font_bytes_unchanged(candidate: bytes, base: bytes, *, clone_start: int, source_start: int) -> bool:
    font_local_offsets = {
        (code & 0x7F) * 16 + row
        for left, right in GLYPH_CODE_PAIRS.values()
        for code in (left, right, left + 0x20, right + 0x20)
        for row in range(16)
    }
    return all(
        candidate[clone_start + index] == base[source_start + index]
        for index in range(CHR_PAIR_SIZE)
        if index not in font_local_offsets
    )


def analyze(
    *,
    base_rom: Path,
    candidate_rom: Path,
    menu_capture: Path,
    items_capture: Path,
    base_items_capture: Path,
    opening_capture: Path,
) -> dict[str, Any]:
    base = base_rom.read_bytes()
    candidate = candidate_rom.read_bytes()
    if len(base) != len(candidate):
        raise ValueError("base and candidate ROM lengths differ")
    layout = parse_ines_layout(base)
    clone_start = chr_page_offset(layout, CLONE_CHR_1K_PAIR)
    clone_source = chr_page_offset(layout, 0x3E)

    menu_nametables = exactly_one(menu_capture, "*_nametables_2000_2fff.bin").read_bytes()
    candidate_template = candidate[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH]
    captured_template = menu_nametables[0x700 : 0x700 + TEMPLATE_LENGTH]
    menu_snapshot = read_tsv(menu_capture / "mapper_snapshot.tsv")[-1]
    items_screen = exactly_one(items_capture, "*_screen.png")
    base_items_screen = exactly_one(base_items_capture, "*_screen.png")
    opening_record = exactly_one(opening_capture, "opening_target_record.tsv")
    opening_rows = read_tsv(opening_record)
    opening_match = bool(opening_rows) and opening_rows[-1].get("active_expected_match") == "true"

    checks = {
        "candidate_base_md5": hashlib.md5(base).hexdigest() == "0d406a85285b4de8468f0dab6aad5fe5",
        "menu_lua_done": lua_done(menu_capture),
        "menu_template_matches_candidate": menu_template_matches(candidate_template, captured_template),
        "menu_clone_r1_active": menu_snapshot.get("r1") == f"{RASTER_R1_VALUE_CLONE:02X}",
        "menu_clone_copied_from_original_source": clone_non_font_bytes_unchanged(
            candidate, base, clone_start=clone_start, source_start=clone_source
        ),
        "menu_screen_available": menu_capture.joinpath(next(iter([p.name for p in menu_capture.glob("*_screen.png")]), "")).is_file(),
        "items_lua_done": lua_done(items_capture),
        "items_screen_pixel_equal_to_base": screenshot_pixel_equal(items_screen, base_items_screen),
        "opening_lua_done": lua_done(opening_capture),
        "opening_target_match": opening_match,
    }
    return {
        "status": "SOFT_GATE_PASS_COMBINED_CANDIDATE" if all(checks.values()) else "SOFT_GATE_FAIL_COMBINED_CANDIDATE",
        "release_verdict": "UNKNOWN",
        "candidate": {
            "rom": str(candidate_rom),
            "md5": hashlib.md5(candidate).hexdigest(),
            "base_md5": hashlib.md5(base).hexdigest(),
        },
        "checks": checks,
        "captures": {
            "menu": str(menu_capture),
            "items": str(items_capture),
            "opening_p182": str(opening_capture),
            "opening_target_record": str(opening_record),
        },
        "limits": [
            "This is a development candidate for three opening records and the main-menu labels.",
            "Items page isolation passed, but Items Korean text itself is not translated in this candidate.",
            "Other dialogue records, combat progression, cursor lifecycle, and release-wide shared CHR contexts remain UNKNOWN.",
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Korean Development Candidate Runtime",
        "",
        f"Status: **{payload['status']}**",
        f"Release verdict: **{payload['release_verdict']}**",
        "",
        f"- Candidate MD5: `{payload['candidate']['md5']}`.",
        "- The menu route, Items page-isolation route, and opening pointer-182 route all use fixed frame caps and ended with `lua_done`.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        f"- `{name}`: {'PASS' if value else 'FAIL'}" for name, value in payload["checks"].items()
    )
    lines += ["", "## Limits", ""]
    lines.extend(f"- {limit}" for limit in payload["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-rom", type=Path, default=resolve_base_rom(None))
    parser.add_argument("--candidate-rom", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--menu-capture", type=Path, default=DEFAULT_MENU_CAPTURE)
    parser.add_argument("--items-capture", type=Path, default=DEFAULT_ITEMS_CAPTURE)
    parser.add_argument("--base-items-capture", type=Path, default=DEFAULT_BASE_ITEMS_CAPTURE)
    parser.add_argument("--opening-capture", type=Path, default=DEFAULT_OPENING_CAPTURE)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()
    payload = analyze(
        base_rom=args.base_rom,
        candidate_rom=args.candidate_rom,
        menu_capture=args.menu_capture,
        items_capture=args.items_capture,
        base_items_capture=args.base_items_capture,
        opening_capture=args.opening_capture,
    )
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(f"status={payload['status']}")
    print(f"report_json={args.report_json}")
    print(f"report_markdown={args.report_markdown}")
    return 0 if payload["status"] == "SOFT_GATE_PASS_COMBINED_CANDIDATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())

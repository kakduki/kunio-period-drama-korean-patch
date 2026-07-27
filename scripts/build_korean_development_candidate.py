#!/usr/bin/env python3
"""Combine the verified opening batch and the bounded main-menu candidate.

The opening candidate owns the dialogue renderer and its Bank 7 glyph bytes.
The menu candidate owns a cloned R1 page.  When those candidates are combined,
the clone must come from the Japanese base ROM, not from the already-modified
opening ROM, or the opening glyphs would leak into the Items action row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_main_menu_korean_candidate import (
    FONT_PROFILE,
    GLYPH_CODE_PAIRS,
    GLYPH_ORDER,
    apply_main_menu_candidate,
    build_square_glyph_tiles,
    default_square_font,
)
from build_opening_dialogue_proof import BASE_MD5, resolve_base_rom
from build_patch import make_records, write_ips
from korean_font_quality import evaluate_release_square_font, render_square_glyph_bitmaps
from rom_utils import REPO_ROOT


DEFAULT_OPENING_ROM = (
    REPO_ROOT
    / "output"
    / "opening_ptr_182_184_16x16_readability"
    / "kunio_period_drama_korean_opening_ptr_182_184_16x16_readability.nes"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "korean_development_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "korean_development_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "korean_development_candidate.md"
DEFAULT_OUT_STEM = "kunio_period_drama_korean_development_candidate"


def changed_offsets(before: bytes, after: bytes) -> list[int]:
    return [index for index, (old, new) in enumerate(zip(before, after)) if old != new]


def build_candidate(
    base: bytes,
    opening: bytes,
    *,
    font_path: Path,
) -> tuple[bytes, list[dict[str, object]], dict[str, object]]:
    if hashlib.md5(base).hexdigest() != BASE_MD5:
        raise ValueError("unsupported base ROM MD5")
    if len(opening) != len(base):
        raise ValueError("opening candidate ROM length differs from base ROM")
    if opening == base:
        raise ValueError("opening candidate must contain the verified opening batch")

    glyph_tiles = build_square_glyph_tiles(
        font_path, GLYPH_CODE_PAIRS, font_profile=FONT_PROFILE
    )
    font_quality = evaluate_release_square_font(
        font_path=font_path,
        font_profile=FONT_PROFILE,
        bitmaps=render_square_glyph_bitmaps(
            font_path, GLYPH_ORDER, font_profile=FONT_PROFILE
        ),
    )
    if font_quality["verdict"] != "PASS":
        raise ValueError("menu font-quality gate failed")

    patched, menu_targets = apply_main_menu_candidate(
        opening,
        glyph_tiles,
        clone_source=base,
    )
    if patched == opening:
        raise AssertionError("menu candidate made no changes")
    opening_changes = changed_offsets(base, opening)
    menu_changes = changed_offsets(opening, patched)
    if not opening_changes or not menu_changes:
        raise AssertionError("combined candidate is missing an owned component")

    return patched, menu_targets, {
        "font_quality": font_quality,
        "opening_change_count": len(opening_changes),
        "menu_change_count": len(menu_changes),
        "total_change_count": len(changed_offsets(base, patched)),
    }


def report_payload(
    *,
    base: bytes,
    opening: bytes,
    patched: bytes,
    menu_targets: list[dict[str, object]],
    details: dict[str, object],
    opening_rom: Path,
    font_path: Path,
    ips_path: Path,
    rom_path: Path,
) -> dict[str, object]:
    return {
        "status": "CANDIDATE_BUILT_PENDING_COMBINED_RUNTIME_SMOKE",
        "base": {
            "md5": hashlib.md5(base).hexdigest(),
            "rom": str(resolve_base_rom(None)),
        },
        "components": {
            "opening_candidate_rom": str(opening_rom),
            "opening_candidate_md5": hashlib.md5(opening).hexdigest(),
            "menu_candidate_targets": menu_targets,
            "menu_clone_source": "original Japanese base ROM",
            "font_path": str(font_path),
            "font_profile": FONT_PROFILE,
            "font_quality": details["font_quality"],
        },
        "candidate": {
            "rom": str(rom_path),
            "ips": str(ips_path),
            "md5": hashlib.md5(patched).hexdigest(),
            "opening_change_count": details["opening_change_count"],
            "menu_change_count": details["menu_change_count"],
            "total_change_count": details["total_change_count"],
        },
        "known_limits": [
            "This combines three opening records and the main-menu label candidate only.",
            "The menu clone is based on the original CHR page so opening glyphs do not leak into Items.",
            "Other dialogue records, gameplay text, cursor lifecycle, and full Items Korean text remain unpromoted.",
        ],
    }


def render_markdown(payload: dict[str, object]) -> str:
    base = payload["base"]
    components = payload["components"]
    candidate = payload["candidate"]
    assert isinstance(base, dict)
    assert isinstance(components, dict)
    assert isinstance(candidate, dict)
    lines = [
        "# Korean Development Candidate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Components",
        "",
        f"- Base ROM MD5: `{base['md5']}`.",
        f"- Opening candidate: `{components['opening_candidate_md5']}`.",
        f"- Menu clone source: **{components['menu_clone_source']}**.",
        f"- Font quality: **{components['font_quality']['verdict']}**.",
        "- The menu clone is copied from the Japanese base before opening glyph changes are layered in.",
        "",
        "## Candidate",
        "",
        f"- ROM: `{candidate['rom']}`.",
        f"- IPS: `{candidate['ips']}`.",
        f"- Candidate MD5: `{candidate['md5']}`.",
        f"- Opening changed bytes: `{candidate['opening_change_count']}`.",
        f"- Menu changed bytes: `{candidate['menu_change_count']}`.",
        f"- Total changed bytes: `{candidate['total_change_count']}`.",
        "",
        "## Limits",
        "",
    ]
    limits = payload["known_limits"]
    assert isinstance(limits, list)
    lines.extend(f"- {limit}" for limit in limits)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=resolve_base_rom(None))
    parser.add_argument("--opening-rom", type=Path, default=DEFAULT_OPENING_ROM)
    parser.add_argument("--font", type=Path, default=Path(r"C:\Windows\Fonts\malgunbd.ttf"))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--out-stem", default=DEFAULT_OUT_STEM)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()

    base_path = args.rom.expanduser().resolve()
    opening_path = args.opening_rom.expanduser().resolve()
    font_path = args.font.expanduser().resolve()
    base = base_path.read_bytes()
    opening = opening_path.read_bytes()
    patched, targets, details = build_candidate(base, opening, font_path=font_path)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{args.out_stem}.ips"
    rom_path = args.out_dir / f"{args.out_stem}.nes"
    write_ips(ips_path, make_records(base, patched))
    rom_path.write_bytes(patched)
    payload = report_payload(
        base=base,
        opening=opening,
        patched=patched,
        menu_targets=targets,
        details=details,
        opening_rom=opening_path,
        font_path=font_path,
        ips_path=ips_path,
        rom_path=rom_path,
    )
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(f"rom={rom_path}")
    print(f"ips={ips_path}")
    print(f"report_json={args.report_json}")
    print(f"candidate_md5={payload['candidate']['md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

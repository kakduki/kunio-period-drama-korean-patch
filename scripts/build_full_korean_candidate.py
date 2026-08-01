#!/usr/bin/env python3
"""Build the Korean candidate by composing the verified renderer families.

The English reference patch uses more than one text renderer.  This builder
keeps the existing full pointer-dialogue compiler as stage one, then applies
the bounded 16x16 main-menu candidate to that expanded ROM as stage two.  It
is intentionally a development candidate: the remaining non-pointer English
records stay listed in the coverage audit until their screen contexts are
implemented and verified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_full_pointer_korean_candidate import (
    DEFAULT_DRAFT,
    DEFAULT_ENGLISH,
    DEFAULT_PLAN,
    DEFAULT_SEGMENTS,
    apply_full_candidate,
    build_config,
    default_tall_font,
)
from build_main_menu_korean_candidate import (
    FONT_PROFILE,
    GLYPH_CODE_PAIRS,
    apply_main_menu_source_page_candidate,
    build_square_glyph_tiles,
    default_square_font,
)
from build_patch import make_records, write_ips
from korean_font_quality import evaluate_release_square_font, render_square_glyph_bitmaps
from rom_utils import REPO_ROOT


DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_candidate.md"
OUT_STEM = "kunio_period_drama_korean_full_candidate"


def render_markdown(payload: dict[str, object]) -> str:
    coverage = payload["coverage"]
    assert isinstance(coverage, dict)
    lines = [
        "# Full Korean Candidate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Composed Stages",
        "",
        "1. Full pointer-dialogue compiler using the English pointer/control skeleton.",
        "2. Bounded 16x16 Korean main-menu template and isolated source-page glyph slots.",
        "",
        f"- Base MD5: `{payload['base_md5']}`.",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Candidate ROM: `{payload['rom_path']}`.",
        f"- Candidate IPS: `{payload['ips_path']}`.",
        f"- Full pointer records: `{payload['pointer']['compiled_records']}`; bytes: `{payload['pointer']['record_bytes']}`.",
        f"- Main-menu targets: `{payload['menu']['target_count']}`.",
        f"- Korean square-font gate: **{payload['menu']['font_quality']['verdict']}**.",
        "",
        "## English Reference Coverage",
        "",
        f"- English changed bytes: `{coverage['english_changed_bytes']}`.",
        f"- Korean bytes inside English record spans: `{coverage['korean_changed_bytes_in_reference_spans']}`.",
        f"- Fully covered records by same-offset audit: `{coverage['covered_records']}`.",
        f"- Partial records: `{coverage['partial_records']}`; missing records: `{coverage['missing_records']}`.",
        "- Same-offset coverage is an ownership audit, not visual or translation proof.",
        "",
        "## Limits",
        "",
        "- This is not a final release ROM.",
        "- Growth, name-table, status, item, technique, and other non-pointer renderers remain open.",
        "- Boot, menu, dialogue, and interaction-route smoke tests are required before promotion.",
        "",
    ]
    return "\n".join(lines)


def build_candidate(
    base: bytes,
    *,
    draft_path: Path = DEFAULT_DRAFT,
    english_path: Path = DEFAULT_ENGLISH,
    plan_path: Path = DEFAULT_PLAN,
    segments_path: Path = DEFAULT_SEGMENTS,
    font_path: str | Path | None = None,
) -> tuple[bytes, dict[str, object]]:
    pointer_config = build_config(base, draft_path, english_path, plan_path, segments_path)
    pointer_font = default_tall_font(font_path)
    pointer_rom, pointer_targets = apply_full_candidate(base, pointer_config, pointer_font)

    menu_font = default_square_font(font_path)
    glyphs = tuple(GLYPH_CODE_PAIRS)
    bitmaps = render_square_glyph_bitmaps(menu_font, glyphs, font_profile=FONT_PROFILE)
    font_quality = evaluate_release_square_font(
        font_path=menu_font,
        font_profile=FONT_PROFILE,
        bitmaps=bitmaps,
    )
    if font_quality["verdict"] != "PASS":
        raise ValueError(f"Korean menu font quality gate failed: {font_quality['checks']}")
    menu_tiles = build_square_glyph_tiles(
        menu_font,
        GLYPH_CODE_PAIRS,
        font_profile=FONT_PROFILE,
    )
    candidate, menu_targets = apply_main_menu_source_page_candidate(pointer_rom, menu_tiles)

    metadata = {
        "pointer": {
            "compiled_records": sum(bool(record["record"]) for record in pointer_config["records"]),
            "record_bytes": pointer_config["record_bytes"],
            "record_start": f"0x{pointer_config['record_start']:05X}",
            "record_end": f"0x{pointer_config['record_end']:05X}",
            "font_pages": len(pointer_config["pages"]),
            "font_path": str(pointer_font),
            "target_count": len(pointer_targets),
        },
        "menu": {
            "font_path": str(menu_font),
            "font_quality": font_quality,
            "target_count": len(menu_targets),
        },
        "targets": {
            "pointer": pointer_targets,
            "menu": menu_targets,
        },
    }
    return candidate, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--english", type=Path, default=DEFAULT_ENGLISH)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--segments", type=Path, default=DEFAULT_SEGMENTS)
    parser.add_argument("--font")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    args = parser.parse_args()

    base_path = Path(args.rom).expanduser().resolve() if args.rom else None
    if base_path is None:
        from build_opening_dialogue_proof import resolve_base_rom

        base_path = resolve_base_rom(None)
    base = base_path.read_bytes()
    candidate, metadata = build_candidate(
        base,
        draft_path=args.draft,
        english_path=args.english,
        plan_path=args.plan,
        segments_path=args.segments,
        font_path=args.font,
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    records = make_records(base, candidate)
    write_ips(ips_path, records)
    rom_path.write_bytes(candidate)
    if apply_ips(base, ips_path) != candidate:
        raise AssertionError("full Korean candidate IPS round trip failed")

    payload: dict[str, object] = {
        "status": "COMPOSED_CANDIDATE_BUILT_RUNTIME_UNKNOWN",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(candidate).hexdigest(),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "patch_record_count": len(records),
        "patch_changed_bytes": sum(len(data) for _offset, data in records),
        "pointer": metadata["pointer"],
        "menu": metadata["menu"],
        "targets": metadata["targets"],
        "coverage": {
            "source": "run scripts/analyze_english_korean_coverage.py against this candidate",
            "english_changed_bytes": None,
            "korean_changed_bytes_in_reference_spans": None,
            "covered_records": None,
            "partial_records": None,
            "missing_records": None,
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(f"rom={rom_path}")
    print(f"ips={ips_path}")
    print(f"candidate_md5={payload['candidate_md5']}")
    print(f"patch_records={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

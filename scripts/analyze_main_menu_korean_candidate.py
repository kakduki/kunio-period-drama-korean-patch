#!/usr/bin/env python3
"""Evaluate the bounded FCEUX smoke capture for the Korean main-menu candidate."""

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
    RASTER_R1_VALUE_CLONE,
    SOURCE_CHR_1K_PAIR,
    TEMPLATE_LENGTH,
    TEMPLATE_ROM_OFFSET,
    build_menu_template,
    chr_page_offset,
)
from build_opening_dialogue_proof import resolve_base_rom
from rom_utils import REPO_ROOT


DISPLAY_TEMPLATE_OFFSET = 0x700
MIRROR_TEMPLATE_OFFSET = 0xF00
DYNAMIC_TEMPLATE_OFFSETS = frozenset({0x21})
DEFAULT_CANDIDATE_ROM = (
    REPO_ROOT
    / "output"
    / "main_menu_korean_candidate"
    / "kunio_period_drama_korean_main_menu_16x16_candidate.nes"
)
DEFAULT_CAPTURE_DIR = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate_capture"
DEFAULT_JSON_OUTPUT = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate_smoke_report.json"
DEFAULT_MARKDOWN_OUTPUT = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate_smoke_report.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def latest_reason(rows: list[dict[str, str]]) -> str | None:
    for row in reversed(rows):
        reason = (row.get("reason") or "").strip()
        if reason:
            return reason
    return None


def matches_template(source: bytes, rendered: bytes) -> bool:
    return len(source) == len(rendered) == TEMPLATE_LENGTH and all(
        source[index] == rendered[index]
        for index in range(TEMPLATE_LENGTH)
        if index not in DYNAMIC_TEMPLATE_OFFSETS
    )


def exactly_one(capture_dir: Path, suffix: str) -> Path:
    matches = sorted(capture_dir.glob(f"*{suffix}"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected exactly one {suffix!r} file in {capture_dir}, found {len(matches)}"
        )
    return matches[0]


def analyze(
    *,
    base_rom_path: Path,
    candidate_rom_path: Path,
    capture_dir: Path,
) -> dict[str, Any]:
    base = base_rom_path.read_bytes()
    candidate = candidate_rom_path.read_bytes()
    if len(base) != len(candidate):
        raise ValueError("base and candidate ROM lengths differ")
    layout = parse_ines_layout(base)
    source_start = chr_page_offset(layout, SOURCE_CHR_1K_PAIR)
    clone_start = chr_page_offset(layout, CLONE_CHR_1K_PAIR)
    expected_template = build_menu_template(base)
    candidate_template = candidate[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH]

    summary_rows = read_tsv(capture_dir / "summary.tsv")
    mapper_rows = read_tsv(capture_dir / "mapper_snapshot.tsv")
    mapper_config_rows = read_tsv(capture_dir / "mapper_config_writes.tsv")
    nametable_path = exactly_one(capture_dir, "_nametables_2000_2fff.bin")
    nametables = nametable_path.read_bytes()
    if len(nametables) != 0x1000:
        raise ValueError(f"unexpected nametable dump size: {len(nametables)}")
    screen_paths = sorted(capture_dir.glob("*_screen.png"))
    snapshot = mapper_rows[-1] if mapper_rows else {}
    display_template = nametables[
        DISPLAY_TEMPLATE_OFFSET : DISPLAY_TEMPLATE_OFFSET + TEMPLATE_LENGTH
    ]
    mirror_template = nametables[
        MIRROR_TEMPLATE_OFFSET : MIRROR_TEMPLATE_OFFSET + TEMPLATE_LENGTH
    ]

    raster_r1_rows = [
        row
        for row in mapper_config_rows
        if row.get("address") == "0503"
        and row.get("value") == f"{RASTER_R1_VALUE_CLONE:02X}"
        and row.get("pc") == "EE51"
    ]
    checks = {
        "candidate_template_matches_declared_layout": candidate_template == expected_template,
        "source_bank7_chr_pair_unchanged": candidate[
            source_start : source_start + CHR_PAIR_SIZE
        ]
        == base[source_start : source_start + CHR_PAIR_SIZE],
        "clone_chr_pair_changed": candidate[clone_start : clone_start + CHR_PAIR_SIZE]
        != base[clone_start : clone_start + CHR_PAIR_SIZE],
        "lua_done": latest_reason(summary_rows) == "lua_done",
        "captured_template_matches_candidate": matches_template(candidate_template, display_template),
        "captured_mirror_matches_candidate": matches_template(candidate_template, mirror_template),
        "final_mapper_r1_is_clone": snapshot.get("r1") == f"{RASTER_R1_VALUE_CLONE:02X}",
        "raster_trace_contains_clone_r1": bool(raster_r1_rows),
        "screen_capture_available": len(screen_paths) == 1,
    }
    return {
        "status": "SOFT_GATE_PASS" if all(checks.values()) else "SOFT_GATE_FAIL",
        "release_verdict": "UNKNOWN",
        "checks": checks,
        "source": {
            "base_rom": str(base_rom_path),
            "candidate_rom": str(candidate_rom_path),
            "base_md5": hashlib.md5(base).hexdigest(),
            "candidate_md5": hashlib.md5(candidate).hexdigest(),
            "template_rom_offset": f"0x{TEMPLATE_ROM_OFFSET:05X}",
            "source_chr_1k_pair": f"0x{SOURCE_CHR_1K_PAIR:02X}",
            "clone_chr_1k_pair": f"0x{CLONE_CHR_1K_PAIR:02X}",
            "expected_final_r1": f"0x{RASTER_R1_VALUE_CLONE:02X}",
        },
        "capture": {
            "dir": str(capture_dir),
            "final_reason": latest_reason(summary_rows),
            "screen": str(screen_paths[0]) if len(screen_paths) == 1 else None,
            "nametables": str(nametable_path),
            "final_mapper_snapshot": snapshot,
            "raster_r1_write_count": len(raster_r1_rows),
        },
        "limits": [
            "This is one fixed menu context, not a broad screen-compatibility audit.",
            "The R1 raster split is shared outside this context; release approval remains UNKNOWN.",
            "Cursor motion and menu return need separate bounded screen captures.",
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    source = payload["source"]
    capture = payload["capture"]
    lines = [
        "# Korean Main Menu Candidate Smoke Test",
        "",
        f"Soft-gate status: **{payload['status']}**",
        f"Release verdict: **{payload['release_verdict']}**",
        "",
        "## Evidence",
        "",
        f"- Candidate MD5: `{source['candidate_md5']}`.",
        f"- Menu capture completion: `{capture['final_reason']}`.",
        f"- Final MMC3 R1: `{capture['final_mapper_snapshot'].get('r1', '')}`; expected `{source['expected_final_r1']}`.",
        f"- Raster R1 clone writes: `{capture['raster_r1_write_count']}`.",
        f"- Screen evidence: `{capture['screen']}`.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        f"- `{name}`: {'PASS' if value else 'FAIL'}"
        for name, value in payload["checks"].items()
    )
    lines += ["", "## Limits", ""]
    lines.extend(f"- {item}" for item in payload["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-rom", type=Path, default=resolve_base_rom(None))
    parser.add_argument("--candidate-rom", type=Path, default=DEFAULT_CANDIDATE_ROM)
    parser.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE_DIR)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    payload = analyze(
        base_rom_path=args.base_rom,
        candidate_rom_path=args.candidate_rom,
        capture_dir=args.capture,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"status={payload['status']}")
    print(f"release_verdict={payload['release_verdict']}")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    return 0 if payload["status"] == "SOFT_GATE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

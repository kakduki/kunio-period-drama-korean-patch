#!/usr/bin/env python3
"""Summarize bounded menu and progression evidence for the full candidate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_main_menu_korean_candidate import SOURCE_CHR_1K_PAIR, TEMPLATE_LENGTH, TEMPLATE_ROM_OFFSET, chr_page_offset
from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_proof import resolve_base_rom
from build_patch import make_records
from rom_utils import REPO_ROOT


DEFAULT_CANDIDATE = (
    REPO_ROOT
    / "output"
    / "full_korean_candidate"
    / "kunio_period_drama_korean_full_candidate.nes"
)
DEFAULT_IPS = (
    REPO_ROOT
    / "output"
    / "full_korean_candidate"
    / "kunio_period_drama_korean_full_candidate.ips"
)
DEFAULT_MENU_CAPTURE = REPO_ROOT / "rom_analysis" / "main_menu_full_korean_candidate_capture"
DEFAULT_PROGRESSION_CAPTURE = REPO_ROOT / "rom_analysis" / "stage_progression_probe_full_korean_candidate"
DEFAULT_POINTER_CAPTURE = REPO_ROOT / "rom_analysis" / "pointer_dialogue_route_probe_full_korean_candidate"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_candidate_smoke_report.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_candidate_smoke_report.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def exactly_one(path: Path, pattern: str) -> Path:
    matches = sorted(path.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one {pattern!r} in {path}, found {len(matches)}")
    return matches[0]


def matches_template(candidate: bytes, rendered: bytes) -> bool:
    if len(rendered) != TEMPLATE_LENGTH:
        return False
    dynamic = {0x21}
    return all(
        candidate[index] == rendered[index]
        for index in range(TEMPLATE_LENGTH)
        if index not in dynamic
    )


def analyze(
    *,
    base_rom: Path,
    candidate_rom: Path,
    ips_path: Path,
    menu_capture: Path,
    progression_capture: Path,
    pointer_capture: Path,
) -> dict[str, object]:
    base = base_rom.read_bytes()
    candidate = candidate_rom.read_bytes()
    ips_round_trip = apply_ips(base, ips_path) == candidate
    menu_nametables = exactly_one(menu_capture, "*_nametables_2000_2fff.bin").read_bytes()
    candidate_template = candidate[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH]
    menu_mapper = read_tsv(menu_capture / "mapper_snapshot.tsv")
    menu_summary = read_tsv(menu_capture / "summary.tsv")
    progression_rows = read_tsv(progression_capture / "captures.tsv")
    progression_summary = read_tsv(progression_capture / "summary.tsv")
    pointer_summary = read_tsv(pointer_capture / "summary.tsv") if (pointer_capture / "summary.tsv").exists() else []
    final_menu_mapper = menu_mapper[-1] if menu_mapper else {}
    final_progression = progression_summary[-1] if progression_summary else {}
    progression_frames = [
        int(row["frame"])
        for row in progression_rows
        if row.get("reason") == "combat_screen_change"
    ]
    event_frames = [
        int(row["frame"])
        for row in progression_rows
        if row.get("reason") == "combat_screen_change" and int(row["frame"]) >= 1900
    ]
    source_start = chr_page_offset(parse_ines_layout(base), SOURCE_CHR_1K_PAIR)
    source_end = source_start + 0x0400
    source_page_changed = candidate[source_start:source_end] != base[source_start:source_end]
    checks = {
        "base_md5": hashlib.md5(base).hexdigest() == "0d406a85285b4de8468f0dab6aad5fe5",
        "candidate_chr_banks_expanded": candidate[5] == 29,
        "ips_round_trip": ips_round_trip,
        "menu_lua_done": bool(menu_summary) and menu_summary[-1].get("reason") == "lua_done",
        "menu_template_display_matches": matches_template(
            candidate_template, menu_nametables[0x700 : 0x700 + TEMPLATE_LENGTH]
        ),
        "menu_template_mirror_matches": matches_template(
            candidate_template, menu_nametables[0xF00 : 0xF00 + TEMPLATE_LENGTH]
        ),
        "menu_r1_restored_original": final_menu_mapper.get("r1") == "3E",
        "source_page_has_korean_changes": source_page_changed,
        "progression_lua_done": bool(final_progression) and final_progression.get("reason") == "lua_done",
        "progression_reaches_combat": bool(progression_frames) and min(progression_frames) <= 915,
        "progression_reaches_late_event": bool(event_frames),
    }
    return {
        "status": "SOFT_GATE_PASS_MENU_AND_GAMEPLAY_ENTRY" if all(checks.values()) else "SOFT_GATE_FAIL",
        "release_verdict": "UNKNOWN",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(candidate).hexdigest(),
        "candidate_rom": str(candidate_rom.relative_to(REPO_ROOT)),
        "candidate_ips": str(ips_path.relative_to(REPO_ROOT)),
        "source_page_rom_range": [source_start, source_end],
        "checks": checks,
        "menu": {
            "capture": str(menu_capture.relative_to(REPO_ROOT)),
            "final_mapper": final_menu_mapper,
            "summary": menu_summary[-1] if menu_summary else {},
        },
        "progression": {
            "capture": str(progression_capture.relative_to(REPO_ROOT)),
            "summary": final_progression,
            "combat_frames": progression_frames,
            "late_event_frames": event_frames,
        },
        "pointer_route": {
            "capture": str(pointer_capture.relative_to(REPO_ROOT)),
            "summary": pointer_summary[-1] if pointer_summary else {},
            "interpretation": "UNKNOWN_TARGET_ROUTE_PROBE_ADDRESS_CONTRACT",
        },
        "limits": [
            "This is a soft-gate development candidate, not a release ROM.",
            "The full 244-row script is compiled, but broad visual proof is not complete.",
            "The pointer route probe uses an older fixed-address target contract and returned UNKNOWN.",
            "The reached gameplay route does not prove boss defeat or every event screen.",
        ],
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Full Korean Candidate Smoke Report",
        "",
        f"Soft-gate status: **{payload['status']}**",
        f"Release verdict: **{payload['release_verdict']}**",
        "",
        f"- Base MD5: `{payload['base_md5']}`.",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Candidate ROM: `{payload['candidate_rom']}`.",
        f"- Candidate IPS: `{payload['candidate_ips']}`.",
        "",
        "## Checks",
        "",
    ]
    checks = payload["checks"]
    assert isinstance(checks, dict)
    lines.extend(f"- `{name}`: {'PASS' if value else 'FAIL'}" for name, value in checks.items())
    lines += [
        "",
        "## Evidence",
        "",
        f"- Menu capture: `{payload['menu']['capture']}`.",
        f"- Progression capture: `{payload['progression']['capture']}`.",
        f"- Pointer route probe: `{payload['pointer_route']['capture']}`; interpretation is UNKNOWN because its fixed target address is stale.",
        "",
        "## Limits",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-rom", type=Path, default=resolve_base_rom(None))
    parser.add_argument("--candidate-rom", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--ips", type=Path, default=DEFAULT_IPS)
    parser.add_argument("--menu-capture", type=Path, default=DEFAULT_MENU_CAPTURE)
    parser.add_argument("--progression-capture", type=Path, default=DEFAULT_PROGRESSION_CAPTURE)
    parser.add_argument("--pointer-capture", type=Path, default=DEFAULT_POINTER_CAPTURE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = analyze(
        base_rom=args.base_rom,
        candidate_rom=args.candidate_rom,
        ips_path=args.ips,
        menu_capture=args.menu_capture,
        progression_capture=args.progression_capture,
        pointer_capture=args.pointer_capture,
    )
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": payload["checks"]}, ensure_ascii=False))
    return 0 if payload["status"] == "SOFT_GATE_PASS_MENU_AND_GAMEPLAY_ENTRY" else 1


if __name__ == "__main__":
    raise SystemExit(main())

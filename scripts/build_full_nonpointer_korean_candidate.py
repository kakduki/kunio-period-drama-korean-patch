#!/usr/bin/env python3
"""Compose the verified non-pointer PRG candidates on top of the full dev candidate.

This is a soft-gate development build. Only runtime-confirmed or
encoding-exact targets with safe equal-length spans are applied.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from build_prg_patch_from_plan import build_prg_patch
from rom_utils import REPO_ROOT, find_rom_path

BASE_ROM = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
INPUT_ROM = REPO_ROOT / "output" / "full_korean_candidate" / "kunio_period_drama_korean_full_candidate.nes"
PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
PADDING = REPO_ROOT / "rom_analysis" / "prg_padding_options.json"
OUT_DIR = REPO_ROOT / "output" / "full_nonpointer_korean_candidate"
OUT_STEM = "kunio_period_drama_korean_full_nonpointer_candidate"
REPORT = REPO_ROOT / "rom_analysis" / "full_nonpointer_korean_candidate.md"


def write_markdown(report: dict[str, object], path: Path) -> None:
    applied = list(report.get("applied", []))
    skipped = list(report.get("skipped", []))
    reasons = Counter(str(row.get("reason", "unknown")) for row in skipped)
    lines = [
        "# Full Non-Pointer Korean Candidate",
        "",
        "This is a soft-gate development candidate composed on top of the full pointer/menu candidate.",
        "",
        f"- Base ROM: {report['original_rom']}",
        f"- Input candidate: {report['font_rom']}",
        f"- Candidate ROM: {report['patched_rom_path']}",
        f"- Candidate IPS: {report['ips_path']}",
        f"- Base MD5: {report['original_md5']}",
        f"- Candidate MD5: {report['patched_md5']}",
        f"- Applied count: {report['applied_count']}",
        f"- Skipped count: {report['skipped_count']}",
        f"- Changed bytes from clean base: {report['changed_bytes_total']}",
        "- Build classification: PASS",
        "- Release classification: UNKNOWN until exact screen visual proof and broader regression coverage.",
        "",
        "## Applied",
        "",
        "| label | ROM offset | source | Korean | old bytes | new bytes | evidence | risk |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in applied:
        lines.append(
            f"| {row.get('label')} | {row.get('rom_hit')} | {row.get('source')} | "
            f"{row.get('korean')} | {row.get('old_bytes')} | {row.get('new_bytes')} | "
            f"{row.get('evidence_level')} | {row.get('risk')} |"
        )
    lines += [
        "",
        "## Exclusion Summary",
        "",
        "Targets requiring a padding rule or only static/pointer-hypothesis evidence remain excluded.",
        "",
        "| reason | count |",
        "| --- | ---: |",
    ]
    for reason, count in sorted(reasons.items()):
        lines.append(f"| {reason} | {count} |")
    lines += [
        "",
        "## Gate",
        "",
        "- Soft gate: PASS for deterministic build generation.",
        "- Boot/progression smoke: run scripts/run_fceux_lua_analysis.py against the candidate.",
        "- Visual proof: UNKNOWN until the two exact source contexts are captured.",
        "- Release: NOT READY.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=str(BASE_ROM))
    parser.add_argument("--input-rom", default=str(INPUT_ROM))
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    parser.add_argument("--out-stem", default=OUT_STEM)
    args = parser.parse_args()

    base_rom = find_rom_path(args.rom).resolve()
    input_rom = Path(args.input_rom).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    report = build_prg_patch(
        base_rom,
        input_rom,
        PLAN,
        PADDING,
        out_dir,
        include_evidence={"runtime-confirmed", "encoding-exact"},
        include_risks={"safe-equal-length"},
        exclude_labels=set(),
        out_stem=args.out_stem,
    )
    write_markdown(report, REPORT)
    print(json.dumps({
        "candidate_rom": report["patched_rom_path"],
        "candidate_ips": report["ips_path"],
        "applied_count": report["applied_count"],
        "skipped_count": report["skipped_count"],
        "patched_md5": report["patched_md5"],
        "report": str(REPORT),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
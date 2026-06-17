#!/usr/bin/env python3
"""Build a v0.4.2 candidate: v0.4.1 PRG edits on the expanded font ROM."""

from __future__ import annotations

import json

from build_prg_patch_from_plan import build_prg_patch
from build_v041_conflict_safe_candidate import V04_EVIDENCE, V04_RISKS, conflict_labels
from rom_utils import REPO_ROOT, find_rom_path


DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
DEFAULT_PADDING = REPO_ROOT / "rom_analysis" / "prg_padding_options.json"
DEFAULT_FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_font_expansion_v0.5_batch32.nes"
DEFAULT_OUT_DIR = REPO_ROOT / "output"
OUT_STEM = "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded"


def main() -> int:
    labels = conflict_labels()
    report = build_prg_patch(
        find_rom_path(None).resolve(),
        DEFAULT_FONT_ROM.resolve(),
        DEFAULT_PLAN.resolve(),
        DEFAULT_PADDING.resolve(),
        DEFAULT_OUT_DIR.resolve(),
        include_evidence=V04_EVIDENCE,
        include_risks=V04_RISKS,
        exclude_labels=labels,
        out_stem=OUT_STEM,
    )
    report_path = DEFAULT_OUT_DIR / f"{OUT_STEM}_build_report.json"
    report["font_expansion_source"] = str(DEFAULT_FONT_ROM)
    report["verdict"] = "manual-test candidate; v0.4.1 PRG edits plus first 32 planned extra glyphs"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"patched ROM: {report['patched_rom_path']}")
    print(f"IPS: {report['ips_path']}")
    print(f"excluded_labels={len(labels)} applied={report['applied_count']} skipped={report['skipped_count']}")
    print(f"patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

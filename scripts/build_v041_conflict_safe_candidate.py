#!/usr/bin/env python3
"""Build a v0.4.1 test candidate excluding v0.4/broad conflicts.

This keeps the v0.4 equal-length/static policy but leaves overlapping records
untouched until manual screen proof decides whether v0.4 or broad interpretation
is correct.
"""

from __future__ import annotations

import json
from pathlib import Path

from build_prg_patch_from_plan import build_prg_patch
from rom_utils import REPO_ROOT, find_rom_path


CONFLICTS = REPO_ROOT / "rom_analysis" / "v04_broad_candidate_conflicts.json"
DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
DEFAULT_PADDING = REPO_ROOT / "rom_analysis" / "prg_padding_options.json"
DEFAULT_FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_plan_v0.2.nes"
DEFAULT_OUT_DIR = REPO_ROOT / "output"
OUT_STEM = "kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe"

V04_EVIDENCE = {
    "encoding-exact",
    "runtime-confirmed",
    "static-candidate",
    "static-candidate+pointer",
}
V04_RISKS = {"safe-equal-length"}


def conflict_labels() -> set[str]:
    data = json.loads(CONFLICTS.read_text(encoding="utf-8"))
    return {
        str(row["v04_label"])
        for row in data.get("conflicts", [])
        if row.get("v04_label")
    }


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
    report["conflict_source"] = str(CONFLICTS)
    report["verdict"] = "manual-test candidate; excludes v0.4/broad overlapping records"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"patched ROM: {report['patched_rom_path']}")
    print(f"IPS: {report['ips_path']}")
    print(f"excluded_labels={len(labels)} applied={report['applied_count']} skipped={report['skipped_count']}")
    print(f"patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

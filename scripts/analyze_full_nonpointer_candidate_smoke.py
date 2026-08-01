#!/usr/bin/env python3
"""Analyze bounded smoke evidence for the composed non-pointer candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT

DEFAULT_ROM = REPO_ROOT / "output" / "full_nonpointer_korean_candidate" / "kunio_period_drama_korean_full_nonpointer_candidate.nes"
DEFAULT_BUILD = REPO_ROOT / "output" / "full_nonpointer_korean_candidate" / "kunio_period_drama_korean_full_nonpointer_candidate_build_report.json"
DEFAULT_TRACE = REPO_ROOT / "rom_analysis" / "stage_progression_probe_full_nonpointer_korean_candidate_trace"
OUT_JSON = REPO_ROOT / "rom_analysis" / "full_nonpointer_korean_candidate_smoke.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "full_nonpointer_korean_candidate_smoke.md"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=str(DEFAULT_ROM))
    parser.add_argument("--build-report", default=str(DEFAULT_BUILD))
    parser.add_argument("--trace-dir", default=str(DEFAULT_TRACE))
    args = parser.parse_args()

    rom = Path(args.rom).resolve()
    build_report_path = Path(args.build_report).resolve()
    trace_dir = Path(args.trace_dir).resolve()
    build_report = json.loads(build_report_path.read_text(encoding="utf-8"))
    summary = (trace_dir / "summary.tsv").read_text(encoding="utf-8", errors="replace")
    captures = (trace_dir / "captures.tsv").read_text(encoding="utf-8", errors="replace")
    rom_bytes = rom.read_bytes()

    checks = {
        "candidate_exists": rom.exists(),
        "candidate_md5_matches_build": md5(rom) == build_report["patched_md5"],
        "candidate_chr_expanded": len(rom_bytes) > 262160 and rom_bytes[5] > 16,
        "build_applied_two_safe_targets": build_report["applied_count"] == 2,
        "fceux_lua_done": "\tlua_done\t" in summary,
        "entry_screen_captured": "entry_screen_change" in captures,
        "combat_screen_captured": "combat_screen_change" in captures,
        "late_event_screen_captured": "1956\tcombat_screen_change" in captures or "2046\tcombat_screen_change" in captures,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "candidate_rom": str(rom),
        "candidate_md5": md5(rom),
        "build_report": str(build_report_path),
        "trace_dir": str(trace_dir),
        "checks": checks,
        "status": status,
        "visual_status": "UNKNOWN",
        "release_status": "NOT_READY",
        "failure_class": "none" if status == "PASS" else "SMOKE_EVIDENCE_MISSING",
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Full Non-Pointer Korean Candidate Smoke",
        "",
        f"- Candidate: {rom}",
        f"- MD5: {result['candidate_md5']}",
        f"- Automated status: {status}",
        "- Visual status: UNKNOWN",
        "- Release status: NOT READY",
        "",
        "| check | result |",
        "| --- | --- |",
    ]
    lines.extend(f"| {name} | {'PASS' if value else 'FAIL'} |" for name, value in checks.items())
    lines += [
        "",
        "The bounded trace reaches lua_done, captures entry screens, reaches combat, and records late event-like screens.",
        "This proves progression smoke only; it does not prove that the two changed strings are visible in their intended screen contexts.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
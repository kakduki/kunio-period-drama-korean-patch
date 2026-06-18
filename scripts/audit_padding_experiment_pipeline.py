#!/usr/bin/env python3
"""Summarize padding-rule experiment evidence for the candidate pipeline."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT


OUT_DIR = REPO_ROOT / "rom_analysis" / "candidate_pipeline"
BUILD_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_padding_exp_build_report.json"
CPU_COMPARISON = REPO_ROOT / "rom_analysis" / "fceux_padding_exp_watch_comparison.json"
PPU_COMPARISON = REPO_ROOT / "rom_analysis" / "fceux_padding_exp_ppu_watch_comparison.json"
CURRENT_FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_font_expansion_v0.5_batch32.nes"
OUT_JSON = OUT_DIR / "padding_experiment_matrix.json"
OUT_CSV = OUT_DIR / "padding_experiment_matrix.csv"
OUT_MD = OUT_DIR / "padding_experiment_matrix.md"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def path_by_name(path_text: str) -> Path:
    path = Path(path_text)
    candidate = REPO_ROOT / "output" / path.name
    if candidate.exists():
        return candidate
    return path


def status_from_cpu(row: dict[str, object] | None) -> str:
    if not row:
        return "UNKNOWN"
    if row.get("final_reason") == "lua_done" and int(row.get("active_expected_matches") or 0) > 0:
        return "PASS"
    if row.get("final_reason"):
        return "UNKNOWN"
    return "FAIL"


def status_from_ppu(row: dict[str, object] | None) -> str:
    if not row:
        return "UNKNOWN"
    if int(row.get("exact_vram_matches") or 0) > 0:
        return "PASS"
    if row.get("final_reason") == "lua_done":
        return "UNKNOWN"
    return "FAIL"


def final_decision(build_status: str, cpu_status: str, ppu_status: str, stale_baseline: bool) -> str:
    if build_status != "PASS":
        return "FAIL_BUILD"
    if cpu_status != "PASS":
        return "FAIL_CPU_ACTIVE_BYTES"
    if ppu_status != "PASS":
        return "UNKNOWN_VISUAL_PADDING_RULE"
    if stale_baseline:
        return "UNKNOWN_REBUILD_ON_CURRENT_FONT_BASE"
    return "PASS_PADDING_RULE_CANDIDATE"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_report = load_json(BUILD_REPORT)
    cpu = load_json(CPU_COMPARISON)
    ppu = load_json(PPU_COMPARISON)
    cpu_by_strategy = {row["strategy"]: row for row in cpu.get("results", [])}
    ppu_by_strategy = {row["strategy"]: row for row in ppu.get("results", [])}

    current_font_md5 = md5(CURRENT_FONT_ROM) if CURRENT_FONT_ROM.exists() else ""
    stale_baseline = bool(current_font_md5 and build_report.get("font_rom_md5") != current_font_md5)

    rows = []
    for build in build_report.get("builds", []):
        strategy = str(build["strategy"])
        rom_path = path_by_name(str(build["rom_path"]))
        ips_path = path_by_name(str(build["ips_path"]))
        build_status = "PASS"
        failure_reason = ""
        if not rom_path.exists():
            build_status = "FAIL"
            failure_reason = "candidate ROM missing"
        elif md5(rom_path) != build.get("patched_md5"):
            build_status = "FAIL"
            failure_reason = "candidate ROM MD5 mismatch"
        elif not ips_path.exists():
            build_status = "FAIL"
            failure_reason = "candidate IPS missing"

        cpu_row = cpu_by_strategy.get(strategy)
        ppu_row = ppu_by_strategy.get(strategy)
        cpu_status = status_from_cpu(cpu_row)
        ppu_status = status_from_ppu(ppu_row)
        rows.append(
            {
                "strategy": strategy,
                "rom_offset": build["rom_hit"],
                "source_japanese": "ちから",
                "korean": "힘",
                "romaji": build.get("source_romaji", "Chikara"),
                "original_bytes": build["original_bytes"],
                "patched_bytes": build["patched_bytes"],
                "pad_bytes": build["pad_bytes"],
                "changes_original_tail": build["changes_original_tail"],
                "build_status": build_status,
                "cpu_active_status": cpu_status,
                "cpu_active_matches": int((cpu_row or {}).get("active_expected_matches") or 0),
                "ppu_exact_status": ppu_status,
                "ppu_exact_vram_matches": int((ppu_row or {}).get("exact_vram_matches") or 0),
                "visual_status": "UNKNOWN",
                "baseline_status": "STALE_FONT_BASE" if stale_baseline else "CURRENT_FONT_BASE",
                "decision": final_decision(build_status, cpu_status, ppu_status, stale_baseline),
                "candidate_rom": str(rom_path.relative_to(REPO_ROOT)) if rom_path.is_relative_to(REPO_ROOT) else str(rom_path),
                "candidate_ips": str(ips_path.relative_to(REPO_ROOT)) if ips_path.is_relative_to(REPO_ROOT) else str(ips_path),
                "failure_reason": failure_reason,
            }
        )

    payload = {
        "source": {
            "build_report": str(BUILD_REPORT.relative_to(REPO_ROOT)),
            "cpu_comparison": str(CPU_COMPARISON.relative_to(REPO_ROOT)),
            "ppu_comparison": str(PPU_COMPARISON.relative_to(REPO_ROOT)),
            "current_font_rom": str(CURRENT_FONT_ROM.relative_to(REPO_ROOT)),
        },
        "summary": {
            "target": "ROM+0x071A4 ちから / Chikara -> 힘",
            "strategy_count": len(rows),
            "all_builds_pass": all(row["build_status"] == "PASS" for row in rows),
            "all_cpu_active_pass": all(row["cpu_active_status"] == "PASS" for row in rows),
            "any_ppu_exact_pass": any(row["ppu_exact_status"] == "PASS" for row in rows),
            "visual_status": "UNKNOWN",
            "baseline_status": "STALE_FONT_BASE" if stale_baseline else "CURRENT_FONT_BASE",
            "font_report_md5": build_report.get("font_rom_md5", ""),
            "current_font_md5": current_font_md5,
            "release_eligible": False,
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fieldnames = list(rows[0]) if rows else []
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Padding Experiment Matrix",
        "",
        "This matrix tracks shortened PRG replacement experiments. These are not release candidates.",
        "",
        f"- Target: `{payload['summary']['target']}`",
        f"- Build artifacts: `{'PASS' if payload['summary']['all_builds_pass'] else 'FAIL'}`",
        f"- CPU active-byte evidence: `{'PASS' if payload['summary']['all_cpu_active_pass'] else 'UNKNOWN'}`",
        f"- PPU exact VRAM evidence: `{'PASS' if payload['summary']['any_ppu_exact_pass'] else 'UNKNOWN'}`",
        f"- Visual status: `{payload['summary']['visual_status']}`",
        f"- Baseline status: `{payload['summary']['baseline_status']}`",
        "",
        "| strategy | patched bytes | build | CPU active | active matches | PPU exact | VRAM matches | baseline | decision |",
        "| --- | --- | --- | --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['strategy']}` | `{row['patched_bytes']}` | {row['build_status']} | "
            f"{row['cpu_active_status']} | {row['cpu_active_matches']} | "
            f"{row['ppu_exact_status']} | {row['ppu_exact_vram_matches']} | "
            f"{row['baseline_status']} | {row['decision']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- `PASS` CPU active-byte evidence means the patched byte sequence was loaded on the known FCEUX route.",
        "- `UNKNOWN` PPU/visual evidence means no padding strategy is safe to promote into the normal dev candidate yet.",
        "- `STALE_FONT_BASE` means the experiment ROMs were built on an older font-expanded base and should be regenerated before another visual pass.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_CSV.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(
        "summary="
        f"builds_pass={payload['summary']['all_builds_pass']} "
        f"cpu_pass={payload['summary']['all_cpu_active_pass']} "
        f"ppu_any={payload['summary']['any_ppu_exact_pass']} "
        f"baseline={payload['summary']['baseline_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

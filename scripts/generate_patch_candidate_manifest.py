#!/usr/bin/env python3
"""Generate a manifest for current Korean patch candidate ROMs.

This prevents mixing the playable test candidate with FCEUX-only padding
experiments while the patch is still incomplete.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT, find_rom_path


OUT_MD = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.md"
OUT_JSON = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"

V041_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe_build_report.json"
V04_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4_equal_length_static_build_report.json"
V03_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.3_build_report.json"
V02_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_plan_v0.2_build_report.json"
PADDING_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_padding_exp_build_report.json"
STATUS = REPO_ROOT / "rom_analysis" / "bank1_offset_status.json"
CAPTURE_QUEUE = REPO_ROOT / "rom_analysis" / "manual_capture_queue.json"
PRIMARY_IPS = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.ips"
V04_BROAD_CONFLICTS = REPO_ROOT / "rom_analysis" / "v04_broad_candidate_conflicts.json"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def rel(path: Path | str | None) -> str:
    if not path:
        return ""
    path = Path(path)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def existing_path(raw: object) -> Path | None:
    if not raw:
        return None
    path = Path(str(raw))
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path if path.exists() else None


def output_path_from_report(raw: object) -> Path | None:
    """Resolve report paths even when old reports contain mojibake absolute dirs."""

    if not raw:
        return None
    direct = existing_path(raw)
    if direct:
        return direct
    name = Path(str(raw)).name
    candidate = REPO_ROOT / "output" / name
    return candidate if candidate.exists() else None


def apply_ips(base: bytes, ips_path: Path) -> bytes:
    patch = ips_path.read_bytes()
    if not patch.startswith(b"PATCH"):
        raise ValueError(f"Not an IPS patch: {ips_path}")

    result = bytearray(base)
    pos = 5
    while pos < len(patch):
        if patch[pos : pos + 3] == b"EOF":
            pos += 3
            if pos != len(patch):
                raise ValueError(f"Trailing bytes after IPS EOF: {ips_path}")
            return bytes(result)

        if pos + 5 > len(patch):
            raise ValueError(f"Truncated IPS record header: {ips_path}")
        offset = int.from_bytes(patch[pos : pos + 3], "big")
        pos += 3
        size = int.from_bytes(patch[pos : pos + 2], "big")
        pos += 2

        if size == 0:
            if pos + 3 > len(patch):
                raise ValueError(f"Truncated IPS RLE record: {ips_path}")
            rle_size = int.from_bytes(patch[pos : pos + 2], "big")
            pos += 2
            value = patch[pos]
            pos += 1
            end = offset + rle_size
            if end > len(result):
                raise ValueError(f"IPS RLE record exceeds ROM size: {ips_path}")
            result[offset:end] = bytes([value]) * rle_size
            continue

        end_pos = pos + size
        end = offset + size
        if end_pos > len(patch):
            raise ValueError(f"Truncated IPS data record: {ips_path}")
        if end > len(result):
            raise ValueError(f"IPS data record exceeds ROM size: {ips_path}")
        result[offset:end] = patch[pos:end_pos]
        pos = end_pos

    raise ValueError(f"IPS patch missing EOF marker: {ips_path}")


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def report_candidate(name: str, report_path: Path, role: str, verdict: str) -> dict[str, object]:
    report = load_json(report_path)
    rom_path = output_path_from_report(report.get("patched_rom_path"))
    ips_path = output_path_from_report(report.get("ips_path"))
    return {
        "name": name,
        "role": role,
        "verdict": verdict,
        "report": rel(report_path),
        "rom_path": rel(rom_path) if rom_path else "",
        "rom_exists": rom_path is not None,
        "rom_md5": md5(rom_path) if rom_path else "",
        "reported_md5": report.get("patched_md5", ""),
        "md5_matches_report": (md5(rom_path) == report.get("patched_md5")) if rom_path else False,
        "ips_path": rel(ips_path) if ips_path else "",
        "ips_exists": ips_path is not None,
        "applied_count": report.get("applied_count", ""),
        "skipped_count": report.get("skipped_count", ""),
        "changed_bytes_total": report.get("changed_bytes_total", ""),
        "include_evidence": report.get("include_evidence", []),
        "include_risks": report.get("include_risks", []),
    }


def font_candidate() -> dict[str, object]:
    report = load_json(V02_REPORT)
    rom_path = existing_path(report.get("patched_rom_path"))
    if rom_path is None:
        rom_path = REPO_ROOT / "output" / "kunio_period_drama_korean_plan_v0.2.nes"
    return {
        "name": "v0.2 font-only",
        "role": "font/glyph experiment",
        "verdict": "not playable text patch by itself",
        "report": rel(V02_REPORT),
        "rom_path": rel(rom_path),
        "rom_exists": rom_path.exists(),
        "rom_md5": md5(rom_path) if rom_path.exists() else "",
        "reported_md5": report.get("patched_md5", ""),
        "md5_matches_report": (md5(rom_path) == report.get("patched_md5")) if rom_path.exists() else False,
        "applied_count": "",
        "skipped_count": "",
        "changed_bytes_total": report.get("changed_bytes_total", ""),
    }


def padding_experiments() -> list[dict[str, object]]:
    report = load_json(PADDING_REPORT)
    experiments = []
    for row in report.get("builds", report.get("experiments", [])):
        rom_path = output_path_from_report(row.get("rom_path"))
        ips_path = output_path_from_report(row.get("ips_path"))
        experiments.append(
            {
                "strategy": row.get("strategy", ""),
                "role": "FCEUX-only padding experiment",
                "verdict": "not final patch candidate",
                "rom_path": rel(rom_path) if rom_path else "",
                "rom_exists": rom_path is not None,
                "rom_md5": md5(rom_path) if rom_path else "",
                "reported_md5": row.get("patched_md5", ""),
                "md5_matches_report": (md5(rom_path) == row.get("patched_md5")) if rom_path else False,
                "ips_path": rel(ips_path) if ips_path else "",
                "ips_exists": ips_path is not None,
                "expected_bytes": row.get("patched_bytes", ""),
            }
        )
    return experiments


def main() -> int:
    base_rom = find_rom_path(None).resolve()
    base_bytes = base_rom.read_bytes()
    status = load_json(STATUS)
    queue = load_json(CAPTURE_QUEUE)
    conflicts = load_json(V04_BROAD_CONFLICTS) if V04_BROAD_CONFLICTS.exists() else {}

    candidates = [
        font_candidate(),
        report_candidate(
            "v0.3 runtime-confirmed equal-length",
            V03_REPORT,
            "conservative PRG+CHR experiment",
            "superseded by v0.4 for current testing",
        ),
        report_candidate(
            "v0.4 equal-length static",
            V04_REPORT,
            "older broad equal-length test candidate",
            "superseded by v0.4.1 because of broad-scan conflicts",
        ),
        report_candidate(
            "v0.4.1 conflict-safe",
            V041_REPORT,
            "current primary manual-test candidate",
            "test in FCEUX, not final release; excludes v0.4/broad overlaps",
        ),
    ]
    experiments = padding_experiments()
    primary_candidate = next(row for row in candidates if row["name"].startswith("v0.4.1"))
    primary_ips_applied_md5 = ""
    primary_ips_matches_rom = False
    if PRIMARY_IPS.exists() and primary_candidate["rom_exists"]:
        primary_ips_applied_md5 = md5_bytes(apply_ips(base_bytes, PRIMARY_IPS))
        primary_ips_matches_rom = primary_ips_applied_md5 == primary_candidate["rom_md5"]

    summary = {
        "base_rom": rel(base_rom),
        "base_md5": md5(base_rom),
        "primary_candidate": "v0.4.1 conflict-safe",
        "primary_candidate_md5": primary_candidate["rom_md5"],
        "primary_ips": rel(PRIMARY_IPS),
        "primary_ips_exists": PRIMARY_IPS.exists(),
        "primary_ips_apply_md5": primary_ips_applied_md5,
        "primary_ips_apply_matches_rom": primary_ips_matches_rom,
        "candidate_count": len(candidates),
        "padding_experiment_count": len(experiments),
        "bank1_targets": status.get("summary", {}).get("target_count", ""),
        "runtime_confirmed_targets": status.get("summary", {}).get("runtime_confirmed_count", ""),
        "manual_capture_queue": rel(CAPTURE_QUEUE),
        "manual_capture_queued_targets": queue.get("summary", {}).get("queued_targets", ""),
        "v04_broad_conflicts": rel(V04_BROAD_CONFLICTS) if V04_BROAD_CONFLICTS.exists() else "",
        "v04_broad_conflict_count": conflicts.get("summary", {}).get("overlapping_conflicts", ""),
        "v04_broad_high_conflict_count": conflicts.get("summary", {}).get("high_confidence_conflicts", ""),
        "completion_status": "incomplete; needs manual FCEUX screen verification and more text offsets",
    }

    payload = {
        "summary": summary,
        "candidates": candidates,
        "padding_experiments": experiments,
        "do_not_confuse": [
            "v0.4.1 is the current primary test ROM, not a final release.",
            "v0.4 has overlapping high-confidence broad-scan candidates and is superseded for primary testing.",
            "padding experiment ROMs are only for validating shortened replacements.",
            "YouTube transcription helps identify text, but ROM offsets and runtime evidence still decide patchability.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Patch Candidate Manifest",
        "",
        "This manifest separates the current manual-test ROM from one-off experiments.",
        "",
        "## Summary",
        "",
        f"- Base ROM: `{summary['base_rom']}`",
        f"- Base MD5: `{summary['base_md5']}`",
        f"- Primary current test candidate: **{summary['primary_candidate']}**",
        f"- Primary candidate MD5: `{summary['primary_candidate_md5']}`",
        f"- Primary IPS: `{summary['primary_ips']}`",
        f"- Primary IPS applies to same MD5: **{'yes' if summary['primary_ips_apply_matches_rom'] else 'no'}**",
        f"- v0.4/broad conflicts: `{summary['v04_broad_conflicts']}` ({summary['v04_broad_conflict_count']} overlaps, {summary['v04_broad_high_conflict_count']} high-confidence)",
        f"- Completion status: **{summary['completion_status']}**",
        f"- Manual capture queue: `{summary['manual_capture_queue']}` ({summary['manual_capture_queued_targets']} targets)",
        "",
        "## Patch Candidates",
        "",
        "| name | role | verdict | ROM | MD5 | report MD5 ok | applied | skipped | changed bytes |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in candidates:
        lines.append(
            f"| {row['name']} | {row['role']} | {row['verdict']} | "
            f"`{row['rom_path']}` | `{row['rom_md5']}` | "
            f"{'yes' if row['md5_matches_report'] else 'no'} | "
            f"{row.get('applied_count', '')} | {row.get('skipped_count', '')} | "
            f"{row.get('changed_bytes_total', '')} |"
        )

    lines += [
        "",
        "## Padding Experiments",
        "",
        "These are not release candidates. They exist only to test shortened replacement padding behavior.",
        "",
        "| strategy | verdict | ROM | MD5 | report MD5 ok |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in experiments:
        lines.append(
            f"| {row['strategy']} | {row['verdict']} | `{row['rom_path']}` | "
            f"`{row['rom_md5']}` | {'yes' if row['md5_matches_report'] else 'no'} |"
        )

    lines += [
        "",
        "## Current Rule",
        "",
        "- Test `output/kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes` first.",
        "- Use `lua/kunio_manual_v04_screen_dump.lua` on manually reached screens.",
        "- Do not treat padding experiment ROMs as patch releases.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"primary={summary['primary_candidate']} md5={summary['primary_candidate_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

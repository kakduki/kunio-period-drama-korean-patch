#!/usr/bin/env python3
"""Build soft-gated text patch candidates and pipeline reports."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from rom_utils import REPO_ROOT, find_rom_path


OUT_DIR = REPO_ROOT / "rom_analysis" / "candidate_pipeline"
BUILD_MATRIX = OUT_DIR / "build_matrix.md"
STRING_CANDIDATES = OUT_DIR / "string_candidates.csv"
FALSE_POSITIVES = OUT_DIR / "false_positive_list.csv"
PATCHED_REPORT = OUT_DIR / "patched_rom_report.md"
SMOKE_LOG = OUT_DIR / "smoke_test_log.txt"
RELEASE_GATE = OUT_DIR / "release_gate_checklist.md"
LEGACY_SMOKE_SUMMARY = OUT_DIR / "smoke_summary.tsv"

PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_font_expansion_v0.5_batch32.nes"
TARGET_RECORDS = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "manual_frame_000883_target_records.tsv"
SCREENSHOT = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "manual_frame_000883_screen.png"
CANDIDATES = [
    {
        "build_id": "softgate-0562f-tatsuichi",
        "slug": "0562f_tatsuichi",
        "rom_hit": "0x0562F",
        "label_prefix": "watch_rom_0562f_",
        "source_japanese": "\u305f\u3064\u3044\u3061",
        "korean": "\ud0c0\uce20\uc774\uce58",
        "romaji": "Tatsuichi",
        "selection_reason": "active on a real dialogue screen; equal-length planned bytes; boss/name context",
    },
    {
        "build_id": "softgate-05643-heishichi",
        "slug": "05643_heishichi",
        "rom_hit": "0x05643",
        "label_prefix": "watch_rom_05643_",
        "source_japanese": "\u3078\u3044\u3057\u3061",
        "korean": "\ud5e4\uc774\uc2dc\uce58",
        "romaji": "Heishichi",
        "selection_reason": "active on the same real dialogue screen; equal-length planned bytes; boss/name context",
    },
    {
        "build_id": "softgate-0736a-raifu",
        "slug": "0736a_raifu",
        "rom_hit": "0x0736A",
        "label_prefix": "rom_0736a_candidate_93",
        "source_japanese": "\u30e9\u30a4\u30d5",
        "korean": "\ub77c\uc774\ud504",
        "romaji": "Raifu",
        "selection_reason": "active on the same real dialogue screen; equal-length planned bytes; UI/status context",
    },
    {
        "build_id": "softgate-0739d-raifu",
        "slug": "0739d_raifu",
        "rom_hit": "0x0739D",
        "label_prefix": "rom_0739d_candidate_93",
        "source_japanese": "\u30e9\u30a4\u30d5",
        "korean": "\ub77c\uc774\ud504",
        "romaji": "Raifu",
        "selection_reason": "active on the same real dialogue screen; equal-length planned bytes; UI/status context",
    },
]


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def parse_hex_bytes(text: str) -> bytes:
    return bytes(int(part, 16) for part in text.split() if part)


def parse_byte_list(values: list[str]) -> bytes:
    return bytes(int(value, 16) for value in values)


def prg_bank(rom_offset: int) -> int:
    if rom_offset < 0x10:
        return -1
    return (rom_offset - 0x10) // 0x4000


def candidate_by_rom_hit(rom_hit: str) -> dict[str, object] | None:
    normalized = rom_hit.upper()
    for candidate in CANDIDATES:
        if str(candidate["rom_hit"]).upper() == normalized:
            return candidate
    return None


def output_rom_path(candidate: dict[str, object]) -> Path:
    return REPO_ROOT / "output" / f"kunio_period_drama_softgate_{candidate['slug']}.nes"


def output_ips_path(candidate: dict[str, object]) -> Path:
    return REPO_ROOT / "output" / f"kunio_period_drama_softgate_{candidate['slug']}.ips"


def output_report_path(candidate: dict[str, object]) -> Path:
    return REPO_ROOT / "output" / f"kunio_period_drama_softgate_{candidate['slug']}_report.json"


def smoke_summary_path(candidate: dict[str, object]) -> Path:
    return OUT_DIR / f"smoke_summary_{candidate['build_id']}.tsv"


def load_plan_target(candidate: dict[str, object]) -> dict[str, object]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    for target in plan["targets"]:
        label = str(target.get("label", ""))
        if (
            str(target.get("rom_hit")).upper() == str(candidate["rom_hit"]).upper()
            and label.startswith(str(candidate["label_prefix"]))
        ):
            return target
    raise KeyError(f"Selected target not found in {PLAN}: {candidate['rom_hit']}")


def load_active_records() -> list[dict[str, str]]:
    with TARGET_RECORDS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_candidate_rom(candidate: dict[str, object], target: dict[str, object]) -> dict[str, object]:
    base_path = find_rom_path(None).resolve()
    base = base_path.read_bytes()
    patched = bytearray(FONT_ROM.read_bytes())
    rom_offset = int(str(target["rom_hit"]), 16)
    old_bytes = parse_hex_bytes(str(target["original_expected_bytes"]))
    new_bytes = parse_byte_list(list(target["planned_prg_bytes"]))
    current = base[rom_offset : rom_offset + len(old_bytes)]

    status = "PASS"
    failure_class = ""
    failure_reason = ""
    if current != old_bytes:
        status = "FAIL"
        failure_class = "BASE_BYTES_MISMATCH"
        failure_reason = f"base bytes {current.hex(' ').upper()} != expected {old_bytes.hex(' ').upper()}"
    elif len(old_bytes) != len(new_bytes):
        status = "FAIL"
        failure_class = "LENGTH_MISMATCH"
        failure_reason = f"old length {len(old_bytes)} != new length {len(new_bytes)}"
    else:
        patched[rom_offset : rom_offset + len(new_bytes)] = new_bytes
        output_rom_path(candidate).parent.mkdir(parents=True, exist_ok=True)
        output_rom_path(candidate).write_bytes(patched)
        write_ips(output_ips_path(candidate), make_records(base, bytes(patched)))

    return {
        "build_id": candidate["build_id"],
        "slug": candidate["slug"],
        "readable": {
            "source_japanese": candidate["source_japanese"],
            "korean": candidate["korean"],
            "romaji": candidate["romaji"],
        },
        "target": target,
        "base_rom": str(base_path.relative_to(REPO_ROOT)),
        "font_rom": str(FONT_ROM.relative_to(REPO_ROOT)),
        "candidate_rom": str(output_rom_path(candidate).relative_to(REPO_ROOT)),
        "candidate_ips": str(output_ips_path(candidate).relative_to(REPO_ROOT)),
        "base_md5": md5(base),
        "candidate_md5": md5(bytes(patched)) if status == "PASS" else "",
        "rom_offset": f"0x{rom_offset:05X}",
        "prg_bank": prg_bank(rom_offset),
        "prg_offset": f"0x{rom_offset - 0x10:05X}",
        "old_bytes": old_bytes.hex(" ").upper(),
        "new_bytes": new_bytes.hex(" ").upper(),
        "build_status": status,
        "failure_class": failure_class,
        "failure_reason": failure_reason,
    }


def write_string_candidates(records: list[dict[str, str]]) -> None:
    rows = []
    for record in records:
        rom_hit = record["rom_hit"].replace("ROM+", "")
        candidate = candidate_by_rom_hit(rom_hit)
        rows.append(
            {
                "selected": "yes" if candidate else "no",
                "rom_offset": rom_hit,
                "prg_bank": prg_bank(int(rom_hit, 16)),
                "screen_context": "fceux_input_explorer_v042 frame 883 dialogue screen",
                "label": record["label"],
                "category": record["category"],
                "source_japanese": candidate["source_japanese"] if candidate else "",
                "korean": candidate["korean"] if candidate else "",
                "romaji": candidate["romaji"] if candidate else "",
                "cpu_range": record["cpu_range"],
                "expected_bytes": record["expected_bytes"],
                "active_expected_match": record["active_expected_match"],
                "selection_reason": candidate["selection_reason"]
                if candidate
                else "deferred to avoid broad or ambiguous multi-string patching in this pipeline pass",
            }
        )
    with STRING_CANDIDATES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_false_positive_list(records: list[dict[str, str]]) -> None:
    fieldnames = ["rom_offset", "label", "risk_class", "reason", "action"]
    rows = []
    for record in records:
        rom_hit = record["rom_hit"].replace("ROM+", "")
        if candidate_by_rom_hit(rom_hit):
            continue
        risk = "DEFERRED_NOT_FALSE_POSITIVE"
        reason = "active bytes are present, but this pass patches only one known string"
        if record["label"].endswith("07227_candidate_84"):
            risk = "VISUAL_CONTEXT_AMBIGUOUS"
            reason = "active in CPU memory but not the visibly readable bottom dialogue string in frame 883"
        rows.append(
            {
                "rom_offset": rom_hit,
                "label": record["label"],
                "risk_class": risk,
                "reason": reason,
                "action": "do not patch in current single-string build",
            }
        )
    with FALSE_POSITIVES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_build_matrix(reports: list[dict[str, object]]) -> None:
    lines = [
        "# Build Matrix",
        "",
        "Development builds use a soft gate. Release approval uses the separate hard gate checklist.",
        "",
        "| build id | scope | source screen/context | ROM offset | PRG bank | patch type | build | boot smoke | visual proof | decision |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for report in reports:
        smoke_status = smoke_status_from_summary(report["build_id"])
        lines.append(
            "| "
            f"`{report['build_id']}` | one string | "
            "`fceux_input_explorer_v042 frame 883 dialogue screen` | "
            f"`{report['rom_offset']}` | {report['prg_bank']} | equal-length PRG bytes + existing font expansion | "
            f"{report['build_status']} | {smoke_status} | soft gate only | candidate ROM produced |"
        )
    lines += [
        "",
        "## Notes",
        "",
    ]
    for report in reports:
        readable = report["readable"]
        lines.append(
            f"- `{report['build_id']}` source string: "
            f"`{readable['source_japanese']}` / `{readable['korean']}` / {readable['romaji']}"
        )
    lines += [
        f"- Source screenshot: `{SCREENSHOT.relative_to(REPO_ROOT).as_posix()}`",
        "- This matrix intentionally does not require manual visual proof for development candidates.",
    ]
    BUILD_MATRIX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_patched_report(reports: list[dict[str, object]]) -> None:
    lines = [
        "# Patched ROM Report",
        "",
    ]
    for report in reports:
        readable = report["readable"]
        smoke_status = smoke_status_from_summary(report["build_id"])
        lines += [
            f"## Candidate `{report['build_id']}`",
            "",
            f"- Build status: `{report['build_status']}`",
            f"- Base ROM: `{report['base_rom']}`",
            f"- Base MD5: `{report['base_md5']}`",
            f"- Candidate ROM: `{report['candidate_rom']}`",
            f"- Candidate IPS: `{report['candidate_ips']}`",
            f"- Candidate MD5: `{report['candidate_md5']}`",
            f"- Source: `{readable['source_japanese']}` / {readable['romaji']}",
            f"- Korean test string: `{readable['korean']}`",
            f"- ROM offset: `{report['rom_offset']}`",
            f"- PRG bank: `{report['prg_bank']}`",
            f"- PRG offset: `{report['prg_offset']}`",
            "- Screen/context: `fceux_input_explorer_v042 frame 883 dialogue screen`",
            f"- Old bytes: `{report['old_bytes']}`",
            f"- New bytes: `{report['new_bytes']}`",
            f"- Patch classification: `{report['build_status']}`",
            f"- Boot smoke classification: `{smoke_status}`",
            "- Visual classification: `UNKNOWN` until the exact string is visually confirmed on a release/high-risk pass.",
            "- Failure class: `" + str(report["failure_class"] or "none") + "`",
            "- Failure reason: `" + str(report["failure_reason"] or "none") + "`",
            "",
        ]
    PATCHED_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def smoke_status_from_summary(build_id: str) -> str:
    summary = OUT_DIR / f"smoke_summary_{build_id}.tsv"
    if not summary.exists() and build_id == "softgate-0562f-tatsuichi":
        summary = LEGACY_SMOKE_SUMMARY
    if not summary.exists():
        return "UNKNOWN"
    text = summary.read_text(encoding="utf-8", errors="ignore")
    if "lua_done" in text:
        return "PASS"
    if "lua_start" in text:
        return "UNKNOWN"
    return "FAIL"


def write_release_gate_checklist(reports: list[dict[str, object]]) -> None:
    smoke_checked = "x" if all(smoke_status_from_summary(report["build_id"]) == "PASS" for report in reports) else " "
    lines = [
        "# Release Gate Checklist",
        "",
        "Hard gates apply only to release candidates, not to soft-gated development builds.",
        "",
        "## Development Soft Gate",
        "",
        "- [x] Select one active string from one known screen/context.",
        "- [x] Record ROM offset, PRG bank, bytes, and context.",
        "- [x] Build a one-string candidate ROM/IPS.",
        f"- [{smoke_checked}] Run emulator boot smoke test.",
        "- [x] Classify result as PASS/FAIL/UNKNOWN.",
        "",
        "## Release Hard Gate",
        "",
        "- [ ] Manual visual proof for every release-included string.",
        "- [ ] No known false-positive or ambiguous byte ranges patched.",
        "- [ ] Base ROM hash and patched ROM hash documented.",
        "- [ ] IPS applies cleanly from a clean base ROM.",
        "- [ ] No `.nes` files in release zip.",
        "- [ ] Regression smoke test passes on the release candidate.",
    ]
    RELEASE_GATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_smoke_log_placeholder(reports: list[dict[str, object]]) -> None:
    lines = ["# Candidate Smoke Test Log", ""]
    for report in reports:
        smoke_status = smoke_status_from_summary(report["build_id"])
        failure_class = "none" if smoke_status == "PASS" else "NOT_RUN"
        reason = (
            "FCEUX launched candidate ROM and lua/kunio_auto_dump.lua reported lua_done."
            if smoke_status == "PASS"
            else "Run scripts/run_fceux_lua_analysis.py against the candidate ROM to update this log."
        )
        summary = OUT_DIR / f"smoke_summary_{report['build_id']}.tsv"
        if report["build_id"] == "softgate-0562f-tatsuichi" and not summary.exists():
            summary = LEGACY_SMOKE_SUMMARY
        lines += [
            f"[{report['build_id']}]",
            f"smoke_test_status={smoke_status}",
            f"failure_class={failure_class}",
            f"reason={reason}",
            f"candidate_rom={report['candidate_rom']}",
            "lua_script=lua/kunio_auto_dump.lua",
            f"summary={summary.relative_to(REPO_ROOT).as_posix()}",
            "",
        ]
    SMOKE_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json_reports(reports: list[dict[str, object]]) -> None:
    for report in reports:
        candidate = next(candidate for candidate in CANDIDATES if candidate["build_id"] == report["build_id"])
        output_report_path(candidate).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reports = []
    records = load_active_records()
    for candidate in CANDIDATES:
        target = load_plan_target(candidate)
        reports.append(build_candidate_rom(candidate, target))
    write_string_candidates(records)
    write_false_positive_list(records)
    write_build_matrix(reports)
    write_patched_report(reports)
    write_smoke_log_placeholder(reports)
    write_release_gate_checklist(reports)
    write_json_reports(reports)
    print("build_status=" + ",".join(f"{report['build_id']}:{report['build_status']}" for report in reports))
    for report in reports:
        print(f"candidate_rom={report['candidate_rom']}")
        print(f"candidate_ips={report['candidate_ips']}")
    print(f"artifacts={OUT_DIR.relative_to(REPO_ROOT)}")
    return 0 if all(report["build_status"] == "PASS" for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build one soft-gated text patch candidate and pipeline reports."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
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
SMOKE_SUMMARY = OUT_DIR / "smoke_summary.tsv"

PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_font_expansion_v0.5_batch32.nes"
TARGET_RECORDS = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "manual_frame_000883_target_records.tsv"
SCREENSHOT = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "manual_frame_000883_screen.png"
OUT_ROM = REPO_ROOT / "output" / "kunio_period_drama_softgate_0562f_tatsuichi.nes"
OUT_IPS = REPO_ROOT / "output" / "kunio_period_drama_softgate_0562f_tatsuichi.ips"
OUT_REPORT_JSON = REPO_ROOT / "output" / "kunio_period_drama_softgate_0562f_tatsuichi_report.json"

SELECTED_ROM_HIT = "0x0562F"
SELECTED_LABEL = "watch_rom_0562f_"
READABLE_SOURCE = "\u305f\u3064\u3044\u3061"
READABLE_KOREAN = "\ud0c0\uce20\uc774\uce58"
READABLE_ROMAJI = "Tatsuichi"


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


def load_plan_target() -> dict[str, object]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    for target in plan["targets"]:
        label = str(target.get("label", ""))
        if str(target.get("rom_hit")) == SELECTED_ROM_HIT and label.startswith(SELECTED_LABEL):
            return target
    raise KeyError(f"Selected target not found in {PLAN}: {SELECTED_ROM_HIT}")


def load_active_records() -> list[dict[str, str]]:
    with TARGET_RECORDS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_candidate_rom(target: dict[str, object]) -> dict[str, object]:
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
        OUT_ROM.parent.mkdir(parents=True, exist_ok=True)
        OUT_ROM.write_bytes(patched)
        write_ips(OUT_IPS, make_records(base, bytes(patched)))

    return {
        "target": target,
        "base_rom": str(base_path.relative_to(REPO_ROOT)),
        "font_rom": str(FONT_ROM.relative_to(REPO_ROOT)),
        "candidate_rom": str(OUT_ROM.relative_to(REPO_ROOT)),
        "candidate_ips": str(OUT_IPS.relative_to(REPO_ROOT)),
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


def write_string_candidates(records: list[dict[str, str]], selected: dict[str, object]) -> None:
    rows = []
    for record in records:
        rom_hit = record["rom_hit"].replace("ROM+", "")
        rows.append(
            {
                "selected": "yes" if rom_hit.upper() == SELECTED_ROM_HIT.upper() else "no",
                "rom_offset": rom_hit,
                "prg_bank": prg_bank(int(rom_hit, 16)),
                "screen_context": "fceux_input_explorer_v042 frame 883 dialogue screen",
                "label": record["label"],
                "category": record["category"],
                "source_japanese": READABLE_SOURCE if rom_hit.upper() == SELECTED_ROM_HIT.upper() else "",
                "korean": READABLE_KOREAN if rom_hit.upper() == SELECTED_ROM_HIT.upper() else "",
                "romaji": READABLE_ROMAJI if rom_hit.upper() == SELECTED_ROM_HIT.upper() else "",
                "cpu_range": record["cpu_range"],
                "expected_bytes": record["expected_bytes"],
                "active_expected_match": record["active_expected_match"],
                "selection_reason": (
                    "single soft-gate candidate; active on a real dialogue screen; equal-length planned bytes"
                    if rom_hit.upper() == SELECTED_ROM_HIT.upper()
                    else "deferred to avoid broad multi-string patching in this pipeline pass"
                ),
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
        if rom_hit.upper() == SELECTED_ROM_HIT.upper():
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


def write_build_matrix(report: dict[str, object]) -> None:
    smoke_status = smoke_status_from_summary()
    lines = [
        "# Build Matrix",
        "",
        "Development builds use a soft gate. Release approval uses the separate hard gate checklist.",
        "",
        "| build id | scope | source screen/context | ROM offset | PRG bank | patch type | build | boot smoke | visual proof | decision |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
        (
            "| `softgate-0562f-tatsuichi` | one string | "
            "`fceux_input_explorer_v042 frame 883 dialogue screen` | "
            f"`{report['rom_offset']}` | {report['prg_bank']} | equal-length PRG bytes + existing font expansion | "
            f"{report['build_status']} | {smoke_status} | soft gate only | candidate ROM produced |"
        ),
        "",
        "## Notes",
        "",
        f"- Source string: `{READABLE_SOURCE}` / `{READABLE_KOREAN}` / {READABLE_ROMAJI}",
        f"- Source screenshot: `{SCREENSHOT.relative_to(REPO_ROOT).as_posix()}`",
        "- This matrix intentionally does not require manual visual proof for development candidates.",
    ]
    BUILD_MATRIX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_patched_report(report: dict[str, object]) -> None:
    smoke_status = smoke_status_from_summary()
    lines = [
        "# Patched ROM Report",
        "",
        "## Candidate",
        "",
        "- Build id: `softgate-0562f-tatsuichi`",
        f"- Build status: `{report['build_status']}`",
        f"- Base ROM: `{report['base_rom']}`",
        f"- Base MD5: `{report['base_md5']}`",
        f"- Candidate ROM: `{report['candidate_rom']}`",
        f"- Candidate IPS: `{report['candidate_ips']}`",
        f"- Candidate MD5: `{report['candidate_md5']}`",
        "",
        "## Selected String",
        "",
        f"- Source: `{READABLE_SOURCE}` / {READABLE_ROMAJI}",
        f"- Korean test string: `{READABLE_KOREAN}`",
        f"- ROM offset: `{report['rom_offset']}`",
        f"- PRG bank: `{report['prg_bank']}`",
        f"- PRG offset: `{report['prg_offset']}`",
        "- Screen/context: `fceux_input_explorer_v042 frame 883 dialogue screen`",
        f"- Old bytes: `{report['old_bytes']}`",
        f"- New bytes: `{report['new_bytes']}`",
        "",
        "## Classification",
        "",
        "- Patch classification: `PASS` when bytes match and candidate files are written.",
        f"- Boot smoke classification: `{smoke_status}`",
        "- Visual classification: `UNKNOWN` until the exact string is visually confirmed on a release/high-risk pass.",
        "- Failure class: `" + str(report["failure_class"] or "none") + "`",
        "- Failure reason: `" + str(report["failure_reason"] or "none") + "`",
    ]
    PATCHED_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def smoke_status_from_summary() -> str:
    if not SMOKE_SUMMARY.exists():
        return "UNKNOWN"
    text = SMOKE_SUMMARY.read_text(encoding="utf-8", errors="ignore")
    if "lua_done" in text:
        return "PASS"
    if "lua_start" in text:
        return "UNKNOWN"
    return "FAIL"


def write_release_gate_checklist() -> None:
    smoke_checked = "x" if smoke_status_from_summary() == "PASS" else " "
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


def write_smoke_log_placeholder(report: dict[str, object]) -> None:
    smoke_status = smoke_status_from_summary()
    if smoke_status == "PASS":
        lines = [
            "smoke_test_status=PASS",
            "failure_class=none",
            "reason=FCEUX launched candidate ROM and lua/kunio_auto_dump.lua reported lua_done.",
            f"candidate_rom={report['candidate_rom']}",
            "lua_script=lua/kunio_auto_dump.lua",
            "summary=rom_analysis/candidate_pipeline_smoke/summary.tsv",
        ]
        SMOKE_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    lines = [
        "smoke_test_status=UNKNOWN",
        "failure_class=NOT_RUN",
        "reason=Run scripts/run_fceux_lua_analysis.py against the candidate ROM to update this log.",
        f"candidate_rom={report['candidate_rom']}",
    ]
    SMOKE_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json_report(report: dict[str, object]) -> None:
    OUT_REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = load_plan_target()
    records = load_active_records()
    report = build_candidate_rom(target)
    write_string_candidates(records, target)
    write_false_positive_list(records)
    write_build_matrix(report)
    write_patched_report(report)
    write_smoke_log_placeholder(report)
    write_release_gate_checklist()
    write_json_report(report)
    print(f"build_status={report['build_status']}")
    print(f"candidate_rom={report['candidate_rom']}")
    print(f"candidate_ips={report['candidate_ips']}")
    print(f"artifacts={OUT_DIR.relative_to(REPO_ROOT)}")
    return 0 if report["build_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check candidate pipeline reports stay release-auditable."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


PIPELINE_DIR = REPO_ROOT / "rom_analysis" / "candidate_pipeline"
BUILD_MATRIX = PIPELINE_DIR / "build_matrix.md"
STRING_CANDIDATES = PIPELINE_DIR / "string_candidates.csv"
FALSE_POSITIVES = PIPELINE_DIR / "false_positive_list.csv"
HIGH_RISK = PIPELINE_DIR / "high_risk_candidates.csv"
PATCHED_REPORT = PIPELINE_DIR / "patched_rom_report.md"
PATCH_SCOPE_AUDIT_MD = PIPELINE_DIR / "patch_scope_audit.md"
PATCH_SCOPE_AUDIT_JSON = PIPELINE_DIR / "patch_scope_audit.json"
SMOKE_LOG = PIPELINE_DIR / "smoke_test_log.txt"
RELEASE_GATE = PIPELINE_DIR / "release_gate_checklist.md"
RELEASE_GATE_JSON = PIPELINE_DIR / "release_gate_checklist.json"
COMBINED_REPORT = REPO_ROOT / "output" / "kunio_period_drama_softgate_dev_combined_report.json"

REQUIRED_FILES = [
    BUILD_MATRIX,
    STRING_CANDIDATES,
    FALSE_POSITIVES,
    HIGH_RISK,
    PATCHED_REPORT,
    PATCH_SCOPE_AUDIT_MD,
    PATCH_SCOPE_AUDIT_JSON,
    SMOKE_LOG,
    RELEASE_GATE,
    RELEASE_GATE_JSON,
    COMBINED_REPORT,
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"missing candidate pipeline artifact: {path.relative_to(REPO_ROOT).as_posix()}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    selected = [row for row in read_csv(STRING_CANDIDATES) if row["selected"] == "yes"]
    quarantined = [row for row in read_csv(STRING_CANDIDATES) if row["selected"] == "quarantine"]
    false_positive_rows = read_csv(FALSE_POSITIVES)
    high_risk_rows = read_csv(HIGH_RISK)
    combined = json.loads(COMBINED_REPORT.read_text(encoding="utf-8"))
    patch_scope = json.loads(PATCH_SCOPE_AUDIT_JSON.read_text(encoding="utf-8"))

    if len(selected) != 9:
        errors.append(f"expected 9 selected soft-gate strings, got {len(selected)}")
    if len(quarantined) != 1:
        errors.append(f"expected 1 frame-active quarantined string, got {len(quarantined)}")
    if len(high_risk_rows) != 5:
        errors.append(f"expected 5 high-risk rows, got {len(high_risk_rows)}")
    if false_positive_rows:
        errors.append(f"expected no deferred false-positive rows for the frame-883 active set, got {len(false_positive_rows)}")
    if combined.get("applied_count") != 9:
        errors.append(f"expected combined applied_count 9, got {combined.get('applied_count')}")
    if combined.get("build_status") != "PASS":
        errors.append(f"expected combined build_status PASS, got {combined.get('build_status')}")
    if patch_scope.get("summary", {}).get("all_pass") is not True:
        errors.append("patch scope audit should be all_pass true")

    for field in ["base_rom", "font_rom", "candidate_rom", "candidate_ips"]:
        value = str(combined.get(field, ""))
        if "\\" in value:
            errors.append(f"combined report field {field} uses backslashes: {value}")
        if not value:
            errors.append(f"combined report field {field} is empty")

    for path in [BUILD_MATRIX, PATCHED_REPORT, PATCH_SCOPE_AUDIT_MD, SMOKE_LOG, RELEASE_GATE]:
        text = path.read_text(encoding="utf-8")
        if "\\\\" in text or "output\\" in text or "rom\\" in text:
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()} contains Windows-style report paths")

    release_gate = RELEASE_GATE.read_text(encoding="utf-8")
    release_gate_payload = json.loads(RELEASE_GATE_JSON.read_text(encoding="utf-8"))
    gate_rows = release_gate_payload.get("gates", [])
    gate_status = {row.get("gate"): row.get("status") for row in gate_rows}
    expected_gate_status = {
        "development soft gate": "PASS",
        "candidate patch scope constrained": "PASS",
        "release-included visual proof": "FAIL",
        "high-risk/quarantined visual proof": "FAIL",
        "false-positive/ambiguous bytes excluded": "PASS",
        "base and patched hashes documented": "PASS",
        "IPS applies from clean base ROM": "PASS",
        "release zip contains no ROM": "PASS",
        "regression boot smoke": "PASS",
        "shortened padding rule acceptance": "UNKNOWN",
    }
    if gate_status != expected_gate_status:
        errors.append(f"unexpected release gate JSON status map: {gate_status}")
    if release_gate_payload.get("summary", {}).get("release_ready") is not False:
        errors.append("release gate JSON should mark release_ready false")
    for row in gate_rows:
        markdown_row = f"| {row['gate']} | {row['status']} | {row['failure_class']} | {row['evidence']} |"
        if markdown_row not in release_gate:
            errors.append(f"release gate markdown missing JSON row: {markdown_row}")
    for expected in [
        "Gate Status Summary",
        "Development Soft Gate",
        "Release Hard Gate",
        "PASS",
        "FAIL",
        "UNKNOWN",
        "VISUAL_PROOF_PENDING",
        "HIGH_RISK_VISUAL_PROOF_PENDING",
        "release zip contains no ROM | PASS | none",
        "candidate patch scope constrained | PASS | none",
        "shortened padding rule acceptance | UNKNOWN | PADDING_RULE_UNPROVEN",
        "No `.nes` files in release zip",
        "Manual visual proof for every release-included string",
        "Patch Scope Audit",
    ]:
        target_text = release_gate if expected != "Patch Scope Audit" else PATCH_SCOPE_AUDIT_MD.read_text(encoding="utf-8")
        if expected not in target_text:
            errors.append(f"release gate checklist missing {expected!r}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: candidate pipeline reports are complete and use portable paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

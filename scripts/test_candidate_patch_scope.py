#!/usr/bin/env python3
"""Check the generated soft-gate candidate patch scope audit."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


AUDIT_JSON = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "patch_scope_audit.json"
AUDIT_MD = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "patch_scope_audit.md"
RELEASE_GATE_JSON = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_checklist.json"
RELEASE_GATE_MD = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_checklist.md"


def main() -> int:
    payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    summary = payload["summary"]
    rows = payload["rows"]
    errors: list[str] = []

    if summary.get("row_count") != 15:
        errors.append(f"expected 15 candidate rows, got {summary.get('row_count')}")
    if summary.get("status_counts") != {"PASS": 15, "FAIL": 0, "SKIP": 0}:
        errors.append(f"unexpected status counts: {summary.get('status_counts')!r}")
    if summary.get("all_pass") is not True:
        errors.append("patch scope audit should pass for all current candidates")

    combined = next((row for row in rows if row.get("build_id") == "softgate-dev-combined"), None)
    if not combined:
        errors.append("combined candidate row missing")
    else:
        if combined.get("changed_offset_count") != 23:
            errors.append(f"combined changed offset count should be 23, got {combined.get('changed_offset_count')}")
        if len(combined.get("expected_spans", [])) != 9:
            errors.append("combined candidate should include 9 expected spans")

    quarantine = next((row for row in rows if row.get("build_id") == "softgate-quarantine-07227-katana"), None)
    if not quarantine:
        errors.append("quarantined Katana row missing")
    elif quarantine.get("expected_spans", [{}])[0].get("rom_offset") != "0x07227":
        errors.append("quarantined Katana row should audit ROM offset 0x07227")

    markdown = AUDIT_MD.read_text(encoding="utf-8")
    release_gate = json.loads(RELEASE_GATE_JSON.read_text(encoding="utf-8"))
    gate_status = {row.get("gate"): row.get("status") for row in release_gate.get("gates", [])}
    if gate_status.get("candidate patch scope constrained") != "PASS":
        errors.append(f"release gate did not record candidate patch scope PASS: {gate_status!r}")
    release_gate_md = RELEASE_GATE_MD.read_text(encoding="utf-8")
    if "candidate patch scope constrained | PASS | none" not in release_gate_md:
        errors.append("release gate markdown missing patch scope PASS row")
    for text in [
        "Patch Scope Audit",
        "softgate-dev-combined",
        "softgate-quarantine-07227-katana",
        "All pass: `True`",
        "0x0569D",
        "0x07227",
    ]:
        if text not in markdown:
            errors.append(f"{text!r} missing from markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: candidate patch scope audit proves candidates only alter planned spans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

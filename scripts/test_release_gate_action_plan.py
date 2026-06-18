#!/usr/bin/env python3
"""Check the release gate action plan matches the open gate status."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


ACTION_JSON = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_action_plan.json"
ACTION_MD = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_action_plan.md"


def main() -> int:
    errors: list[str] = []
    payload = json.loads(ACTION_JSON.read_text(encoding="utf-8"))
    summary = payload["summary"]
    actions = payload["actions"]

    if summary.get("open_gate_count") != 3:
        errors.append(f"expected 3 open gates, got {summary.get('open_gate_count')}")
    if summary.get("action_count") != 3:
        errors.append(f"expected 3 actions, got {summary.get('action_count')}")
    if summary.get("next_gate") != "release-included visual proof":
        errors.append(f"unexpected next gate: {summary.get('next_gate')!r}")
    if summary.get("release_ready") is not False:
        errors.append("release gate action plan should keep release_ready false")

    expected = [
        ("release-included visual proof", "VISUAL_PROOF_PENDING", 10),
        ("high-risk/quarantined visual proof", "HIGH_RISK_VISUAL_PROOF_PENDING", 20),
        ("shortened padding rule acceptance", "PADDING_RULE_UNPROVEN", 30),
    ]
    actual = [(row["gate"], row["failure_class"], row["priority"]) for row in actions]
    if actual != expected:
        errors.append(f"unexpected action ordering: {actual!r}")

    markdown = ACTION_MD.read_text(encoding="utf-8")
    for expected_text in [
        "Release Gate Action Plan",
        "release-included visual proof",
        "high-risk/quarantined visual proof",
        "shortened padding rule acceptance",
        "0x07227",
        "audit_padding_experiment_pipeline.py",
    ]:
        if expected_text not in markdown:
            errors.append(f"{expected_text!r} missing from action plan markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: release gate action plan maps open gates to concrete next actions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

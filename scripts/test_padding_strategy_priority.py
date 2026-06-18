#!/usr/bin/env python3
"""Check the generated padding strategy priority report."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


PRIORITY_JSON = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "padding_strategy_priority.json"
PRIORITY_MD = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "padding_strategy_priority.md"


def main() -> int:
    payload = json.loads(PRIORITY_JSON.read_text(encoding="utf-8"))
    summary = payload["summary"]
    rows = payload["rows"]
    errors: list[str] = []

    if summary.get("current_font_strategy_count") != 5:
        errors.append(f"expected 5 current-font strategies, got {summary.get('current_font_strategy_count')}")
    if summary.get("recommended_strategy") != "preserve_tail":
        errors.append(f"expected preserve_tail recommendation, got {summary.get('recommended_strategy')!r}")
    if summary.get("recommended_risk_class") != "LOWEST_STRUCTURAL_RISK":
        errors.append(f"unexpected recommended risk class: {summary.get('recommended_risk_class')!r}")
    if summary.get("release_gate_status") != "UNKNOWN":
        errors.append("padding strategy priority must not promote the release gate")
    if [row["strategy"] for row in rows] != ["preserve_tail", "pad_00", "pad_7a", "pad_f8f9", "pad_ff"]:
        errors.append(f"unexpected strategy ordering: {[row['strategy'] for row in rows]!r}")

    markdown = PRIORITY_MD.read_text(encoding="utf-8")
    for text in [
        "Padding Strategy Priority",
        "Recommended strategy: `preserve_tail`",
        "LOWEST_STRUCTURAL_RISK",
        "Release gate status: `UNKNOWN`",
        "Do not merge shortened replacements",
    ]:
        if text not in markdown:
            errors.append(f"{text!r} missing from markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: padding strategy priority keeps the gate UNKNOWN and ranks preserve_tail first")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

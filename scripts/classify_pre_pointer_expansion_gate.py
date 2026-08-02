#!/usr/bin/env python3
"""Classify the bounded pre-pointer expansion against its route baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rom_utils import REPO_ROOT

DEFAULT_CANDIDATE_REPORT = REPO_ROOT / "rom_analysis" / "pre_pointer_full_pointer_owner_candidate.json"
DEFAULT_BASELINE_SUMMARY = REPO_ROOT / "rom_analysis" / "stage_progression_probe_full_korean_expanded_candidate" / "summary.tsv"
DEFAULT_CANDIDATE_SUMMARY = REPO_ROOT / "rom_analysis" / "stage_progression_probe_pre_pointer_full_pointer_owner_candidate" / "summary.tsv"
DEFAULT_OUTPUT = REPO_ROOT / "rom_analysis" / "pre_pointer_expansion_runtime_gate.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pre_pointer_expansion_runtime_gate.md"


def read_summary(path: Path) -> dict[str, object]:
    rows = path.read_text(encoding="utf-8-sig").splitlines()
    if len(rows) < 2:
        raise ValueError(f"summary is empty: {path}")
    header = rows[0].split("\t")
    values = rows[-1].split("\t")
    row = dict(zip(header, values))
    captures = path.parent / "captures.tsv"
    capture_text = captures.read_text(encoding="utf-8-sig") if captures.exists() else ""
    return {
        "summary": str(path),
        "last_frame": int(row.get("frame", "0")),
        "reason": row.get("reason", ""),
        "unique_screens": int(row.get("unique", "0")),
        "last_fingerprint": row.get("last_fingerprint", ""),
        "has_combat": "combat_screen_change" in capture_text,
    }


def classify(candidate_report: Path, baseline_summary: Path, candidate_summary: Path, output: Path, markdown: Path) -> dict[str, object]:
    report = json.loads(candidate_report.read_text(encoding="utf-8-sig"))
    baseline = read_summary(baseline_summary)
    candidate = read_summary(candidate_summary)
    route_pass = candidate["unique_screens"] >= baseline["unique_screens"] and candidate["has_combat"]
    payload: dict[str, object] = {
        "status": "PASS" if route_pass else "FAIL",
        "failure_class": "none" if route_pass else "ROUTE_REGRESSION_OR_FALSE_POSITIVE_DATA_OWNERSHIP",
        "candidate_report": str(candidate_report),
        "candidate_rom": report.get("candidate_rom", ""),
        "candidate_md5": report.get("candidate_md5", ""),
        "baseline": baseline,
        "candidate": candidate,
        "candidate_build": {
            "patched_count": report.get("patched_count", 0),
            "new_glyph_count": len(report.get("new_glyphs", [])),
            "status_counts": report.get("status_counts", {}),
        },
        "decision": (
            "Keep the existing pointer-owner candidate as the runnable baseline; quarantine this expansion until each row has runtime ownership evidence."
            if not route_pass
            else "Candidate can proceed to per-screen visual review."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Pre-Pointer Expansion Runtime Gate",
        "",
        f"- Result: {payload['status']}.",
        f"- Failure class: {payload['failure_class']}.",
        f"- Candidate MD5: {payload['candidate_md5']}.",
        f"- Candidate build changed {payload['candidate_build']['patched_count']} additional rows and allocated {payload['candidate_build']['new_glyph_count']} new glyphs.",
        "",
        "| run | unique screens | combat evidence | final reason |",
        "| --- | ---: | --- | --- |",
        f"| baseline pointer-owner candidate | {baseline['unique_screens']} | {baseline['has_combat']} | {baseline['reason']} |",
        f"| expanded pre-pointer candidate | {candidate['unique_screens']} | {candidate['has_combat']} | {candidate['reason']} |",
        "",
        "## Decision",
        "",
        str(payload["decision"]),
        "",
        "The failed run is evidence that fixed FF-delimited bytes are not automatically safe text. The next promotion unit must have a source-owner read and screen-context match before it is included in the runnable candidate.",
    ]
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-report", type=Path, default=DEFAULT_CANDIDATE_REPORT)
    parser.add_argument("--baseline-summary", type=Path, default=DEFAULT_BASELINE_SUMMARY)
    parser.add_argument("--candidate-summary", type=Path, default=DEFAULT_CANDIDATE_SUMMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = classify(args.candidate_report.resolve(), args.baseline_summary.resolve(), args.candidate_summary.resolve(), args.output.resolve(), args.markdown.resolve())
    print(json.dumps({"status": payload["status"], "failure_class": payload["failure_class"], "candidate_md5": payload["candidate_md5"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
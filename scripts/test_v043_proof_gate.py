#!/usr/bin/env python3
"""Test the v0.4.3 proof gate without launching FCEUX."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_v043_from_broad_scan_proof import (
    DEFAULT_PROOF_PACKET,
    DEFAULT_V042_ROM,
    build_candidate,
)
from rom_utils import find_rom_path


TARGET_ROM = "0x0440C"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summary(match: bool) -> dict[str, object]:
    rows = []
    if match:
        rows.append(
            {
                "task": 1,
                "kind": "non_overlapping_needs_manual_screen",
                "confidence": "medium",
                "label": "broad_0440c_kajiya",
                "rom_offset": TARGET_ROM,
                "source_display": "かじや",
                "korean_display": "대장간",
                "expected_original_bytes": "CA D0 E9",
                "planned_prg_bytes": "B5 93 AB",
                "cpu_range": "$83FC-$8400",
                "record_snapshot": "CA D0 E9",
                "decision": "manual_visual_context_required",
            }
        )
    return {
        "status": "matches_need_visual_screen_context" if match else "no_active_original_byte_matches",
        "promotable_after_visual_review": rows,
    }


def review(approved: bool) -> dict[str, object]:
    return {
        "purpose": "test review",
        "rows": [
            {
                "task": 1,
                "rom_offset": TARGET_ROM,
                "label": "broad_0440c_kajiya",
                "romaji": "Kajiya",
                "source_display": "かじや",
                "korean_display": "대장간",
                "visual_context_confirmed": approved,
                "screen_context": "test screen" if approved else "",
                "reviewer_note": "unit test" if approved else "",
            }
        ],
    }


def run_case(tmp: Path, name: str, *, cpu_match: bool, visual: bool) -> dict[str, object]:
    summary_path = tmp / name / "summary.json"
    review_path = tmp / name / "visual_review.json"
    out_dir = tmp / name / "out"
    write_json(summary_path, summary(cpu_match))
    write_json(review_path, review(visual))
    return build_candidate(
        base_rom=find_rom_path(None).resolve(),
        v042_rom=DEFAULT_V042_ROM.resolve(),
        proof_packet_path=DEFAULT_PROOF_PACKET.resolve(),
        summary_path=summary_path,
        review_path=review_path,
        out_dir=out_dir,
        out_stem=f"{name}_candidate",
    )


def assert_no_build(report: dict[str, object], label: str) -> None:
    if report["applied_count"] != 0 or "ips_path" in report:
        raise AssertionError(f"{label}: gate should not build, got {report}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kunio_v043_gate_") as raw:
        tmp = Path(raw)
        assert_no_build(run_case(tmp, "visual_only", cpu_match=False, visual=True), "visual_only")
        assert_no_build(run_case(tmp, "cpu_only", cpu_match=True, visual=False), "cpu_only")
        report = run_case(tmp, "both", cpu_match=True, visual=True)
        if report["applied_count"] != 1:
            raise AssertionError(f"both: expected one applied row, got {report['applied_count']}")
        if "ips_path" not in report or "patched_md5" not in report:
            raise AssertionError(f"both: expected built candidate fields, got {report}")
        applied = report["applied"][0]
        if applied["rom_offset"] != TARGET_ROM or applied["new_bytes"] != "B5 93 AB":
            raise AssertionError(f"both: unexpected applied row {applied}")
    print("OK: v0.4.3 proof gate requires both CPU-read and visual-context evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

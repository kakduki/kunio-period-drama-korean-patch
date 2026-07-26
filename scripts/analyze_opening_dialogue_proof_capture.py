#!/usr/bin/env python3
"""Classify a bounded FCEUX capture for the opening dialogue proof candidate."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_INPUT = REPO_ROOT / "rom_analysis" / "opening_dialogue_proof_capture"
DEFAULT_JSON = DEFAULT_INPUT / "analysis.json"
DEFAULT_MARKDOWN = DEFAULT_INPUT / "analysis.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def analyze_capture(
    input_dir: Path,
    *,
    visual_verdict: str = "UNKNOWN",
    visual_note: str = "",
) -> dict[str, object]:
    visual_verdict = visual_verdict.upper()
    if visual_verdict not in {"PASS", "FAIL", "UNKNOWN"}:
        raise ValueError("visual_verdict must be PASS, FAIL, or UNKNOWN")
    summary = read_tsv(input_dir / "summary.tsv")
    reads = read_tsv(input_dir / "opening_target_reads.tsv")
    record = read_tsv(input_dir / "opening_target_record.tsv")
    screenshots = sorted(input_dir.glob("opening_dialogue_frame_*_screen.*"))
    nametables = sorted(input_dir.glob("opening_dialogue_frame_*_nametable_2000_23bf.bin"))
    final_reason = summary[-1].get("reason", "") if summary else ""
    read_match = any(row.get("active_expected_match", "").lower() == "true" for row in reads)
    record_match = any(row.get("active_expected_match", "").lower() == "true" for row in record)
    boot_pass = final_reason == "lua_done" and bool(screenshots)
    runtime_pass = read_match or record_match
    smoke_pass = boot_pass and runtime_pass
    return {
        "status": (
            "PROOF_CANDIDATE_VISUALLY_VERIFIED"
            if smoke_pass and visual_verdict == "PASS"
            else "CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED"
        ),
        "input_dir": str(input_dir),
        "checks": {
            "bounded_lua_completion": "PASS" if final_reason == "lua_done" else "FAIL",
            "screen_capture": "PASS" if screenshots else "FAIL",
            "nametable_capture": "PASS" if nametables else "FAIL",
            "target_record_runtime_read": "PASS" if runtime_pass else "FAIL",
            "visual_korean_glyph_review": visual_verdict,
        },
        "evidence": {
            "final_reason": final_reason or "MISSING",
            "registered_read_hits": len(reads),
            "matched_read_hits": sum(
                row.get("active_expected_match", "").lower() == "true" for row in reads
            ),
            "matched_capture_record": record_match,
            "screenshots": [str(path) for path in screenshots],
            "nametables": [str(path) for path in nametables],
            "visual_note": visual_note,
        },
        "overall_smoke": "PASS" if smoke_pass else "FAIL",
        "overall_proof": "PASS" if smoke_pass and visual_verdict == "PASS" else "UNKNOWN",
    }


def render_markdown(payload: dict[str, object]) -> str:
    checks = payload["checks"]
    evidence = payload["evidence"]
    lines = [
        "# Opening Dialogue Proof Smoke Test",
        "",
        f"Overall smoke result: **{payload['overall_smoke']}**",
        f"Overall proof result: **{payload['overall_proof']}**",
        "",
        "| check | result |",
        "| --- | --- |",
    ]
    for label, result in checks.items():
        lines.append(f"| {label} | {result} |")
    lines.extend(
        [
            "",
            f"- Final Lua reason: `{evidence['final_reason']}`",
            f"- Registered target read hits: `{evidence['registered_read_hits']}`",
            f"- Matched target read hits: `{evidence['matched_read_hits']}`",
            f"- Visual note: {evidence['visual_note'] or 'None'}",
            "",
            "The visual verdict is recorded separately from boot/runtime evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument(
        "--visual-verdict",
        choices=("pass", "fail", "unknown"),
        default="unknown",
        help="Result of inspecting the captured PNG; defaults to unknown.",
    )
    parser.add_argument("--visual-note", default="")
    args = parser.parse_args()
    payload = analyze_capture(
        args.input_dir,
        visual_verdict=args.visual_verdict,
        visual_note=args.visual_note,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"overall_smoke={payload['overall_smoke']}")
    print(f"overall_proof={payload['overall_proof']}")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    return 0 if payload["overall_smoke"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

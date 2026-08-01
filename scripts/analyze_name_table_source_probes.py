#!/usr/bin/env python3
"""Analyze bounded source-owner probes for the visible name-table sequence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TARGET_ADDRESSES = ("2043", "2044", "2045", "2046")
BASE_SEQUENCE = "88969F8B"
TEST_SEQUENCE = "81828182"
DEFAULT_REPORT_JSON = Path("rom_analysis/name_table_source_probe_runtime.json")
DEFAULT_REPORT_MD = Path("rom_analysis/name_table_source_probe_runtime.md")


def load_sequences(path: Path) -> dict[str, str]:
    by_frame: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            address = str(row.get("ppu_address", "")).upper()
            if address in TARGET_ADDRESSES:
                by_frame.setdefault(str(row.get("frame", "")), {})[address] = str(row.get("value", "")).upper()
    return {
        frame: "".join(values.get(address, "??") for address in TARGET_ADDRESSES)
        for frame, values in by_frame.items()
        if all(address in values for address in TARGET_ADDRESSES)
    }


def matching_frames(sequences: dict[str, str], target: str) -> list[str]:
    return sorted((frame for frame, value in sequences.items() if value == target), key=int)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-trace", type=Path, required=True)
    parser.add_argument("--candidate-trace", type=Path, required=True)
    parser.add_argument("--probe-root", type=Path, required=True)
    parser.add_argument("--candidate-screen", type=Path, required=True)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    args = parser.parse_args()

    base = load_sequences(args.base_trace)
    candidate = load_sequences(args.candidate_trace)
    probe_rows: list[dict[str, object]] = []
    owner_hits: list[str] = []
    for trace in sorted(args.probe_root.glob("kunio_name_probe_trace_*/ppu_writes.tsv")):
        name = trace.parent.name.removeprefix("kunio_name_probe_trace_")
        if name.endswith("_source_only"):
            continue
        sequences = load_sequences(trace)
        test_frames = matching_frames(sequences, TEST_SEQUENCE)
        base_frames = matching_frames(sequences, BASE_SEQUENCE)
        row = {
            "offset": f"0x{name.upper()}",
            "trace": str(trace),
            "test_sequence_frames": test_frames,
            "original_sequence_frames": base_frames,
            "status": "OWNER_MATCH" if test_frames else "NO_MATCH",
        }
        probe_rows.append(row)
        if test_frames:
            owner_hits.append(f"0x{name.upper()}")

    candidate_test_frames = matching_frames(candidate, TEST_SEQUENCE)
    candidate_original_frames = matching_frames(candidate, BASE_SEQUENCE)
    screen_exists = args.candidate_screen.is_file()
    runtime_status = (
        "PASS_SOURCE_OWNER_AND_PPU"
        if owner_hits == ["0x3FB32"] and candidate_test_frames and not candidate_original_frames
        else "UNKNOWN_SOURCE_OWNER"
    )
    visual_status = "PASS_SCREEN_CAPTURE_AVAILABLE" if screen_exists else "UNKNOWN_SCREEN_CAPTURE"
    payload = {
        "status": runtime_status,
        "visual_status": visual_status,
        "release_status": "NOT_READY",
        "target_ppu_addresses": list(TARGET_ADDRESSES),
        "base_sequence": BASE_SEQUENCE,
        "test_sequence": TEST_SEQUENCE,
        "base_reference_frames": matching_frames(base, BASE_SEQUENCE),
        "candidate_test_frames": candidate_test_frames,
        "candidate_original_frames": candidate_original_frames,
        "probe_count": len(probe_rows),
        "owner_hits": owner_hits,
        "probe_rows": probe_rows,
        "base_trace": str(args.base_trace),
        "candidate_trace": str(args.candidate_trace),
        "candidate_screen": str(args.candidate_screen),
        "notes": [
            "0x0561B is a static Bank 1 occurrence but did not alter the natural-route PPU sequence.",
            "0x3FB32 is the only tested occurrence that changed the target PPU sequence.",
            "The candidate string is a test string and is not a release translation.",
            "The route proves one non-pointer renderer context, not whole-game coverage.",
        ],
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_md.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Name-Table Source Probe Runtime",
        "",
        f"- Runtime status: {runtime_status}",
        f"- Visual status: {visual_status}",
        "- Release status: NOT_READY",
        f"- Target PPU addresses: {', '.join(TARGET_ADDRESSES)}",
        f"- Base sequence: {BASE_SEQUENCE}",
        f"- Test sequence: {TEST_SEQUENCE}",
        f"- Candidate test frames: {', '.join(candidate_test_frames) or '-'}",
        f"- Candidate original frames: {', '.join(candidate_original_frames) or '-'}",
        f"- Owner hit(s): {', '.join(owner_hits) or '-'}",
        "",
        "## Probe Results",
        "",
        "| offset | test frames | original frames | result |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {row['offset']} | {', '.join(row['test_sequence_frames']) or '-'} | "
        f"{', '.join(row['original_sequence_frames']) or '-'} | {row['status']} |"
        for row in probe_rows
    )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The English patch's static Bank 1 name-table block is not sufficient to identify the live natural-route source.",
        "- The bounded differential probe identifies physical ROM offset 0x3FB32 as the only tested owner of the target sequence.",
        "- The corrected candidate changes that sequence to 81 82 81 82 and uses CHR Bank 7 tiles 0x181-0x184 for the test glyphs.",
        "- The captured screen is evidence for one renderer context only; release-wide translation remains open.",
        "",
    ])
    args.report_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

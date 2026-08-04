#!/usr/bin/env python3
"""Classify a bounded native manifest-candidate loader trace."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from generate_manifest_runtime_target import read_target


EXPECTED_TARGETS = {
    182: {"start": 0x9FB4, "length": 26, "dialogue_id": 0xB7},
    185: {"start": 0x9FCE, "length": 11, "dialogue_id": 0xBA},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_hex(value: str) -> int:
    return int(value.removeprefix("$"), 16)


def analyze_trace(trace_dir: Path, candidate: Path | None = None, pointer_indices: list[int] | None = None) -> dict[str, object]:
    if candidate is None:
        expected_targets = EXPECTED_TARGETS
    else:
        rom = candidate.read_bytes()
        indices = pointer_indices or sorted(EXPECTED_TARGETS)
        expected_targets = {
            index: {
                "start": int(read_target(rom, index, 0x200)["record_rom_offset"] - 0x04010 + 0x8000),
                "length": len(read_target(rom, index, 0x200)["bytes"]),
                "dialogue_id": index + 1,
            }
            for index in indices
        }
    summary_rows = read_tsv(trace_dir / "summary.tsv")
    loader_rows = read_tsv(trace_dir / "loader_reads.tsv")
    record_rows = read_tsv(trace_dir / "record_reads.tsv")
    final = summary_rows[-1] if summary_rows else {}
    candidate_rows = [
        row for row in record_rows if row.get("label", "").startswith("candidate_record_window")
    ]
    candidate_addresses = [parse_hex(row["address"]) for row in candidate_rows]
    target_results: dict[str, dict[str, object]] = {}
    for index, expected in expected_targets.items():
        addresses = [
            address
            for address in candidate_addresses
            if expected["start"] <= address < expected["start"] + expected["length"]
        ]
        target_results[str(index)] = {
            "start": f"0x{expected['start']:04X}",
            "length": expected["length"],
            "dialogue_id": f"0x{expected['dialogue_id']:02X}",
            "unique_reads": len(set(addresses)),
            "expected_reads": len(addresses) == expected["length"]
            and len(set(addresses)) == expected["length"],
        }

    ids = [parse_hex(row["value"]) for row in loader_rows if row.get("label") == "dialogue_id"]
    distinct_ids: list[int] = []
    for value in ids:
        if not distinct_ids or distinct_ids[-1] != value:
            distinct_ids.append(value)
    progression = all(value in distinct_ids for value in (expected["dialogue_id"] for expected in expected_targets.values()))
    target_reads_pass = all(result["expected_reads"] for result in target_results.values())
    status = "PASS" if final.get("reason") == "lua_done" and progression and target_reads_pass else "UNKNOWN"
    return {
        "status": status,
        "final_reason": final.get("reason", "missing"),
        "final_frame": int(final.get("frame", "-1")),
        "hook_execs": int(final.get("hook_execs", "0")),
        "loader_reads": int(final.get("loader_reads", "0")),
        "candidate_record_reads": len(candidate_rows),
        "dialogue_id_sequence": [f"0x{value:02X}" for value in distinct_ids],
        "expected_progression": progression,
        "targets": target_results,
    }


def render_markdown(payload: dict[str, object]) -> str:
    targets = payload["targets"]
    assert isinstance(targets, dict)
    lines = [
        "# Manifest Loader Trace",
        "",
        f"Status: **{payload['status']}**",
        "",
        f"- Final reason/frame: `{payload['final_reason']}` / `{payload['final_frame']}`.",
        f"- Loader hook executions: `{payload['hook_execs']}`.",
        f"- Candidate record reads: `{payload['candidate_record_reads']}`.",
        f"- Dialogue ID progression: `{', '.join(payload['dialogue_id_sequence'])}`.",
        "",
        "| pointer | CPU | expected bytes | unique reads | result |",
        "|---:|---:|---:|---:|---|",
    ]
    for index, result in targets.items():
        assert isinstance(result, dict)
        lines.append(
            f"| {index} | `${result['start'][2:]}` | {result['length']} | "
            f"{result['unique_reads']} | {'PASS' if result['expected_reads'] else 'UNKNOWN'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--pointer-index", type=int, action="append")
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()
    args.json_out.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    payload = analyze_trace(args.trace.expanduser().resolve(), args.candidate.expanduser().resolve() if args.candidate else None, args.pointer_index)
    args.json_out.expanduser().resolve().write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.markdown_out.expanduser().resolve().write_text(
        render_markdown(payload), encoding="utf-8"
    )
    print(f"status={payload['status']}")
    print(f"candidate_record_reads={payload['candidate_record_reads']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

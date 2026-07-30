#!/usr/bin/env python3
"""Audit display-segment lengths in the full pointer Korean candidate."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_full_pointer_korean_candidate import SOURCE_CODES, build_config
from build_ptr181_bank8_page_probe import resolve_base_rom
from rom_utils import REPO_ROOT


HARD_CELL_LIMIT = 24
WARNING_CELL_LIMIT = 20
DISPLAY_BREAKS = frozenset({0xBB, 0xCA, 0xF8, 0xF9, 0xFF})
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "full_pointer_korean_layout_audit.json"
DEFAULT_CSV = REPO_ROOT / "rom_analysis" / "full_pointer_korean_layout_audit.csv"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_pointer_korean_layout_audit.md"


def display_segment_lengths(record: bytes) -> list[int]:
    lengths: list[int] = []
    current = 0
    for value in record:
        if value in DISPLAY_BREAKS:
            if current:
                lengths.append(current)
                current = 0
        else:
            # Count unknown retained punctuation/variable bytes conservatively.
            current += 1
    if current:
        lengths.append(current)
    return lengths


def build_audit(config: dict[str, object]) -> dict[str, object]:
    records = config["records"]
    assert isinstance(records, list)
    rows: list[dict[str, object]] = []
    for record in records:
        raw = record["record"]
        assert isinstance(raw, bytes)
        if not raw or record["excluded"]:
            continue
        lengths = display_segment_lengths(raw)
        maximum = max(lengths, default=0)
        rows.append(
            {
                "pointer_index": record["pointer_index"],
                "page_index": record["page_index"],
                "segment_lengths": lengths,
                "max_segment_cells": maximum,
                "level": (
                    "FAIL"
                    if maximum > HARD_CELL_LIMIT
                    else "WARN"
                    if maximum > WARNING_CELL_LIMIT
                    else "PASS"
                ),
                "korean_text": record["korean_text"],
            }
        )
    failures = [row for row in rows if row["level"] == "FAIL"]
    warnings = [row for row in rows if row["level"] == "WARN"]
    return {
        "status": "PASS" if not failures else "FAIL",
        "policy": {
            "hard_cell_limit": HARD_CELL_LIMIT,
            "warning_cell_limit": WARNING_CELL_LIMIT,
            "break_codes": [f"0x{value:02X}" for value in sorted(DISPLAY_BREAKS)],
            "counting": "all retained bytes between breaks count as one cell",
            "source_code_count": len(SOURCE_CODES),
        },
        "coverage": {
            "active_records": len(rows),
            "failure_count": len(failures),
            "warning_count": len(warnings),
            "maximum_segment_cells": max(
                (int(row["max_segment_cells"]) for row in rows), default=0
            ),
        },
        "warnings": warnings,
        "failures": failures,
        "records": rows,
    }


def write_outputs(
    payload: dict[str, object],
    json_path: Path,
    csv_path: Path,
    markdown_path: Path,
) -> None:
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    records = payload["records"]
    assert isinstance(records, list)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "pointer_index",
                "page_index",
                "segment_lengths",
                "max_segment_cells",
                "level",
                "korean_text",
            ),
        )
        writer.writeheader()
        for row in records:
            output = dict(row)
            output["segment_lengths"] = ",".join(
                str(value) for value in row["segment_lengths"]
            )
            writer.writerow(output)

    coverage = payload["coverage"]
    warnings = payload["warnings"]
    assert isinstance(coverage, dict) and isinstance(warnings, list)
    lines = [
        "# Full Pointer Korean Layout Audit",
        "",
        f"Status: **{payload['status']}**",
        "",
        f"- Active records: `{coverage['active_records']}`",
        f"- Maximum segment: `{coverage['maximum_segment_cells']}` / `{HARD_CELL_LIMIT}` cells",
        f"- Hard failures: `{coverage['failure_count']}`",
        f"- Warnings over {WARNING_CELL_LIMIT} cells: `{coverage['warning_count']}`",
        "",
        "| pointer | page | segment cells | max | Korean draft |",
        "| ---: | ---: | --- | ---: | --- |",
    ]
    for row in warnings:
        lines.append(
            f"| {row['pointer_index']} | {row['page_index']} | "
            f"`{','.join(str(value) for value in row['segment_lengths'])}` | "
            f"{row['max_segment_cells']} | {row['korean_text']} |"
        )
    lines += [
        "",
        "The count is conservative: retained punctuation and variable bytes count",
        "as cells. This is a static development gate, not a substitute for release",
        "screenshots.",
        "",
    ]
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = build_audit(build_config(resolve_base_rom(args.rom).read_bytes()))
    write_outputs(payload, args.json, args.csv, args.markdown)
    print(
        f"status={payload['status']} "
        f"max={payload['coverage']['maximum_segment_cells']} "
        f"warnings={payload['coverage']['warning_count']} "
        f"failures={payload['coverage']['failure_count']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

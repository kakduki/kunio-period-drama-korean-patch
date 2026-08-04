#!/usr/bin/env python3
"""Produce JSON, CSV, and Markdown evidence for a binary comparison."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _analysis_common import (  # noqa: E402
    changed_spans,
    hashes,
    hex_preview,
    likelihoods,
    load,
    parse_ines,
    pointer_candidates,
    region_for,
)


def build_rows(before: bytes, after: bytes) -> tuple[dict[str, object], list[dict[str, object]]]:
    layout = parse_ines(before)
    rows: list[dict[str, object]] = []
    for index, (start, end) in enumerate(changed_spans(before, after), 1):
        old = before[start:end] if start < len(before) else b""
        new = after[start:end] if start < len(after) else after[start:end]
        region = region_for(start, layout)
        scores = likelihoods(old, new, region)
        rows.append(
            {
                "region_id": index,
                "start": f"0x{start:06X}",
                "end_exclusive": f"0x{end:06X}",
                "start_decimal": start,
                "end_exclusive_decimal": end,
                "length": end - start,
                "region": region,
                "original_hex": hex_preview(old),
                "changed_hex": hex_preview(new),
                "string_likelihood": scores["string"],
                "graphics_likelihood": scores["graphics"],
                "code_likelihood": scores["code"],
                "adjacent_pointer_candidates": pointer_candidates(after, start, end),
            }
        )
    summary = {
        "base": hashes(before),
        "candidate": hashes(after),
        "size_delta": len(after) - len(before),
        "changed_bytes": sum(int(row["length"]) for row in rows),
        "contiguous_regions": len(rows),
        "rom_expanded": len(after) != len(before),
        "layout": layout,
    }
    return summary, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("rom_analysis/binary_diff"))
    args = parser.parse_args()
    before = load(args.base.resolve())
    after = load(args.candidate.resolve())
    summary, rows = build_rows(before, after)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "binary_diff.json").write_text(json.dumps({"summary": summary, "regions": rows}, indent=2) + "\n", encoding="utf-8")
    with (out / "binary_diff.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["region_id", "start", "end_exclusive", "length", "region", "original_hex", "changed_hex", "string_likelihood", "graphics_likelihood", "code_likelihood"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})
    lines = [
        "# Binary Diff",
        "",
        f"- Changed bytes: `{summary['changed_bytes']}`",
        f"- Contiguous regions: `{summary['contiguous_regions']}`",
        f"- ROM expanded: `{summary['rom_expanded']}` (delta `{summary['size_delta']}`)",
        f"- Base MD5: `{summary['base']['md5']}`",
        f"- Candidate MD5: `{summary['candidate']['md5']}`",
        "",
        "| region | range | length | owner candidate | string | graphics | code |",
        "|---:|---|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['region_id']} | `{row['start']}-{row['end_exclusive']}` | {row['length']} | {row['region']} | "
            f"{row['string_likelihood']} | {row['graphics_likelihood']} | {row['code_likelihood']} |"
        )
    (out / "binary_diff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"changed_bytes={summary['changed_bytes']}")
    print(f"regions={summary['contiguous_regions']}")
    print(f"output={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

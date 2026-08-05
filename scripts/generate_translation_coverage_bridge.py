#!/usr/bin/env python3
"""Join readable Korean translation entries with static ROM scan candidates."""
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import Counter
from pathlib import Path


def normalize_source(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").strip()
    # The kana scanner applies this known transcription normalization.
    return value.replace("し", "し")


def load_candidates(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for key in ("top_new_hits", "top_known_hits", "top_menu_title_hits"):
        for row in data.get(key, []):
            item = dict(row)
            item["candidate_pool"] = key
            rows.append(item)
    return rows


def make_rows(reference: list[dict], candidates: list[dict], skipped: list[dict]) -> list[dict]:
    by_source: dict[str, list[dict]] = {}
    by_normalized: dict[str, list[dict]] = {}
    for candidate in candidates:
        source = normalize_source(candidate.get("source", ""))
        normalized = normalize_source(candidate.get("normalized", source))
        by_source.setdefault(source, []).append(candidate)
        by_normalized.setdefault(normalized, []).append(candidate)

    skipped_sources = {normalize_source(row.get("source", "")) for row in skipped}
    output: list[dict] = []
    for index, entry in enumerate(reference, start=1):
        source = normalize_source(entry.get("source", ""))
        candidates_for_entry = by_source.get(source, [])
        match_mode = "exact_source"
        if not candidates_for_entry:
            candidates_for_entry = by_normalized.get(source, [])
            match_mode = "normalized_source" if candidates_for_entry else "none"
        offsets = sorted({row.get("rom_offset", "") for row in candidates_for_entry if row.get("rom_offset")})
        scores = [int(row.get("score", 0)) for row in candidates_for_entry]
        pools = sorted({row.get("candidate_pool", "") for row in candidates_for_entry})
        if source in skipped_sources:
            status = "skipped_by_scanner"
        elif not candidates_for_entry:
            status = "no_static_candidate"
        elif any(row.get("known_bank1_target") for row in candidates_for_entry):
            status = "static_candidate_known_bank1"
        else:
            status = "static_candidate_unverified"
        output.append({
            "translation_index": index,
            "source": entry.get("source", ""),
            "romaji": entry.get("romaji", ""),
            "korean": entry.get("korean", ""),
            "category": entry.get("category", ""),
            "section": entry.get("section", ""),
            "candidate_count": len(candidates_for_entry),
            "candidate_offsets": ";".join(offsets),
            "best_score": max(scores, default=""),
            "candidate_pools": ";".join(pools),
            "match_mode": match_mode,
            "status": status,
            "runtime_status": "not_runtime_proven",
        })
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict], source_paths: tuple[Path, Path]) -> None:
    counts = Counter(row["status"] for row in rows)
    with_candidates = sum(row["candidate_count"] > 0 for row in rows)
    lines = [
        "# Translation Coverage Bridge",
        "",
        "This report joins the readable Korean translation list to static ROM scan candidates.",
        "It does not promote any candidate to a patch target: runtime proof is required.",
        "",
        "## Inputs",
        "",
        f"- Translation reference: `{source_paths[0]}`",
        f"- Pattern scan: `{source_paths[1]}`",
        f"- Translation entries: **{len(rows)}**",
        f"- Entries with at least one static candidate: **{with_candidates}**",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"| `{status}` | {count} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- `static_candidate_known_bank1` means the scan intersects an existing Bank 1 candidate pool; it is not runtime proof.",
        "- `static_candidate_unverified` means a byte-pattern hit exists outside the known Bank 1 target set.",
        "- `no_static_candidate` means the current scanner found no safe byte-pattern candidate, not that the text is absent from the ROM.",
        "- `skipped_by_scanner` means the scanner intentionally excluded the entry, usually because it has too few encodable kana.",
        "- Every row remains `not_runtime_proven` until CPU read, screen/context, and candidate build evidence are recorded.",
        "",
        "Detailed rows: `translation_coverage_bridge.csv` and `translation_coverage_bridge.json`.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=Path("text_data/translation_readable_reference.json"))
    parser.add_argument("--scan", type=Path, default=Path("rom_analysis/translation_pattern_scan.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("rom_analysis"))
    args = parser.parse_args()
    reference_data = json.loads(args.reference.read_text(encoding="utf-8"))
    scan_data = json.loads(args.scan.read_text(encoding="utf-8"))
    rows = make_rows(reference_data["translation_data_joined"], load_candidates(args.scan), scan_data.get("skipped", []))
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "translation_coverage_bridge.json").write_text(json.dumps({
        "source": "translation_readable_reference.json + translation_pattern_scan.json",
        "summary": {"translation_entries": len(rows), "status_counts": dict(Counter(row["status"] for row in rows))},
        "rows": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(output_dir / "translation_coverage_bridge.csv", rows)
    write_markdown(output_dir / "translation_coverage_bridge.md", rows, (args.reference, args.scan))
    print(f"translation_entries={len(rows)}")
    print("status_counts=" + json.dumps(dict(Counter(row["status"] for row in rows)), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
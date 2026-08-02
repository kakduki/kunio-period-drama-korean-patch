#!/usr/bin/env python3
"""Classify pre-pointer records using bounded FCEUX source-read evidence."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_SCAN = REPO_ROOT / "rom_analysis" / "pre_pointer_runtime_scan_pointer_owner"
DEFAULT_TARGETS = REPO_ROOT / "rom_analysis" / "pre_pointer_runtime_targets.json"
DEFAULT_OUTPUT_JSON = REPO_ROOT / "rom_analysis" / "pre_pointer_runtime_gate.json"
DEFAULT_OUTPUT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pre_pointer_runtime_gate.md"
DEFAULT_BASELINE_STAGE = REPO_ROOT / "rom_analysis" / "stage_progression_probe_full_korean_expanded_candidate_with_dialogue_start"
RENDER_SOURCE_PCS = {"$8205", "$8209"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def route_unique(summary_dir: Path) -> int | None:
    summary = summary_dir / "summary.tsv"
    if not summary.exists():
        return None
    rows = read_tsv(summary)
    if not rows:
        return None
    try:
        return int(rows[-1]["unique"])
    except (KeyError, TypeError, ValueError):
        return None


def structural_probe_dir(root: Path, target_id: str) -> Path | None:
    suffix = target_id.lower()
    short_suffix = suffix.removeprefix("en-pre-")
    candidates = [
        root / f"stage_progression_probe_structural_{suffix}_with_dialogue_start",
        root / f"stage_progression_probe_runtime_{short_suffix}_candidate_with_dialogue_start",
        root / f"stage_progression_probe_structural_{suffix}",
        root / f"stage_progression_probe_runtime_{short_suffix}_candidate",
    ]
    return next((path for path in candidates if (path / "summary.tsv").exists()), None)


def classify(scan_dir: Path, targets_path: Path, baseline_stage: Path = DEFAULT_BASELINE_STAGE) -> dict[str, object]:
    target_payload = json.loads(targets_path.read_text(encoding="utf-8"))
    targets = {str(row["id"]): row for row in target_payload.get("targets", [])}
    reads = read_tsv(scan_dir / "source_reads.tsv")
    ppu_rows = read_tsv(scan_dir / "ppu_writes.tsv")
    reads_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in reads:
        reads_by_target[row["target"]].append(row)
    ppu_by_frame = Counter(int(row["frame"]) for row in ppu_rows)

    rows: list[dict[str, object]] = []
    approved_ids: list[str] = []
    counts: Counter[str] = Counter()
    baseline_unique = route_unique(baseline_stage)
    for target_id in sorted(targets):
        target = targets[target_id]
        target_reads = reads_by_target.get(target_id, [])
        pcs = sorted({row["pc"] for row in target_reads})
        text = str(target.get("english_text", "")).replace("<FF>", "").strip()
        probe_dir = structural_probe_dir(baseline_stage.parent, target_id) if target_reads else None
        probe_unique = route_unique(probe_dir) if probe_dir else None
        route_regression = baseline_unique is not None and probe_unique is not None and probe_unique < baseline_unique
        if not target_reads:
            classification = "STATIC_ONLY"
        elif not text:
            classification = "RUNTIME_SOURCE_READ_EMPTY_OR_DATA"
        elif route_regression:
            classification = "RUNTIME_SOURCE_READ_ROUTE_REGRESSION"
        elif RENDER_SOURCE_PCS.intersection(pcs):
            classification = "RUNTIME_SOURCE_READ"
            approved_ids.append(target_id)
        else:
            classification = "RUNTIME_SOURCE_READ_UNKNOWN_PC"
        first_frame = min((int(row["frame"]) for row in target_reads), default=None)
        last_frame = max((int(row["frame"]) for row in target_reads), default=None)
        ppu_near_first = 0
        if first_frame is not None:
            ppu_near_first = sum(ppu_by_frame.get(frame, 0) for frame in range(first_frame - 2, first_frame + 3))
        counts[classification] += 1
        rows.append({
            "record_id": target_id,
            "rom_offset": target["rom_offset"],
            "cpu_addr": target["cpu_addr"],
            "english_text": target["english_text"],
            "read_count": len(target_reads),
            "pcs": pcs,
            "first_read_frame": first_frame,
            "last_read_frame": last_frame,
            "ppu_writes_near_first_read": ppu_near_first,
            "source_capture": (scan_dir / f"{target_id}_source_screen.gd").exists(),
            "structural_probe": str(probe_dir) if probe_dir else None,
            "baseline_unique": baseline_unique,
            "probe_unique": probe_unique,
            "route_regression": route_regression,
            "classification": classification,
        })

    summary_rows = read_tsv(scan_dir / "summary.tsv")
    final_summary = summary_rows[-1] if summary_rows else {}
    return {
        "status": "CLASSIFIED_PRE_POINTER_RUNTIME_SCAN",
        "release_status": "NOT_READY",
        "scan_dir": str(scan_dir),
        "targets_path": str(targets_path),
        "target_count": len(targets),
        "approved_ids": approved_ids,
        "approved_count": len(approved_ids),
        "classification_counts": dict(counts),
        "render_source_pcs": sorted(RENDER_SOURCE_PCS),
        "baseline_unique": baseline_unique,
        "final_summary": final_summary,
        "rows": rows,
        "gate_rule": "Approve only non-empty records read by the known Bank 1 render-source PCs $8205/$8209 whose single-record structural probe does not regress the baseline route.",
    }


def write_markdown(payload: dict[str, object], path: Path) -> None:
    lines = [
        "# Pre-Pointer Runtime Gate",
        "",
        f"- Targets scanned: `{payload['target_count']}`.",
        f"- Runtime-approved records: `{payload['approved_count']}`.",
        f"- Approved IDs: `{', '.join(payload['approved_ids'])}`.",
        f"- Classification counts: `{json.dumps(payload['classification_counts'], sort_keys=True)}`.",
        "- Release status: `NOT_READY`; this is a soft development gate, not visual release approval.",
        "",
        "A record is approved here only when a non-empty target was read by the known Bank 1 render-source PCs `$8205` or `$8209` and its single-record structural probe does not regress the baseline route. Static memory presence alone is insufficient.",
        "",
        "| record | offset | text | reads | PCs | first frame | PPU writes near first read | route probe | classification |",
        "| --- | --- | --- | ---: | --- | ---: | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['record_id']} | `{row['rom_offset']}` | {row['english_text']} | {row['read_count']} | {','.join(row['pcs'])} | {row['first_read_frame'] if row['first_read_frame'] is not None else '-'} | {row['ppu_writes_near_first_read']} | {row['probe_unique'] if row['probe_unique'] is not None else '-'} | {row['classification']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan-dir", type=Path, default=DEFAULT_SCAN)
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    parser.add_argument("--baseline-stage", type=Path, default=DEFAULT_BASELINE_STAGE)
    args = parser.parse_args()
    payload = classify(args.scan_dir.resolve(), args.targets.resolve(), args.baseline_stage.resolve())
    args.output_json.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output_json.resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, args.output_markdown.resolve())
    print(json.dumps({
        "status": payload["status"],
        "approved_count": payload["approved_count"],
        "approved_ids": payload["approved_ids"],
        "classification_counts": payload["classification_counts"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

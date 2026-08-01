#!/usr/bin/env python3
"""Classify pre-pointer inventory rows against English dialogue owners."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_INVENTORY = REPO_ROOT / "rom_analysis" / "pre_pointer_korean_candidates.json"
DEFAULT_REFERENCE = REPO_ROOT / "rom_analysis" / "english_patch_reference.json"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "pre_pointer_dialogue_overlap.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pre_pointer_dialogue_overlap.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MARKDOWN)
    return parser.parse_args()


def overlap_class(start: int, end: int, owners: list[dict[str, object]]) -> str:
    if not owners:
        return "NO_OVERLAP"
    if any(owner["start"] <= start and end <= owner["end"] for owner in owners):
        return "FULLY_CONTAINED"
    if any(start <= owner["start"] and owner["end"] <= end for owner in owners):
        return "RUN_INSIDE_ROW"
    return "EDGE_OVERLAP"


def audit(inventory_path: Path, reference_path: Path) -> dict[str, object]:
    inventory = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    reference = json.loads(reference_path.read_text(encoding="utf-8-sig"))
    raw_owners = reference["english_dialogue_tile_alpha_runs"]
    owners = []
    for index, owner in enumerate(raw_owners):
        start = int(owner["rom_offset"])
        owners.append(
            {
                "owner_index": index,
                "start": start,
                "end": start + int(owner["length"]),
                "rom_offset": f"0x{start:05X}",
                "length": int(owner["length"]),
                "text": owner["text"],
                "prg_bank": owner.get("prg_bank"),
            }
        )

    rows: list[dict[str, object]] = []
    summary = Counter()
    readiness_summary = Counter()
    for row in inventory["rows"]:
        start = int(str(row["rom_offset"]), 16)
        length = len(bytes.fromhex(str(row["raw_bytes"])))
        end = start + length
        hits = []
        for owner in owners:
            overlap = max(0, min(end, owner["end"]) - max(start, owner["start"]))
            if overlap:
                hits.append(
                    {
                        "owner_index": owner["owner_index"],
                        "rom_offset": owner["rom_offset"],
                        "length": owner["length"],
                        "text": owner["text"],
                        "overlap_bytes": overlap,
                        "exactly_contains_row": owner["start"] <= start and end <= owner["end"],
                    }
                )
        classification = overlap_class(start, end, [owner for owner in owners if any(
            hit["owner_index"] == owner["owner_index"] for hit in hits
        )])
        item = {
            "record_id": row["record_id"],
            "readiness": row["readiness"],
            "rom_offset": f"0x{start:05X}",
            "length": length,
            "english_text": row["english_text"],
            "korean_text": row["korean_text"],
            "control_bytes": row["control_bytes"],
            "missing_glyphs": row["missing_glyphs"],
            "overlap_class": classification,
            "owners": hits,
        }
        rows.append(item)
        summary[classification] += 1
        readiness_summary[f"{row['readiness']}:{classification}"] += 1

    patch_candidates = [
        row["record_id"]
        for row in rows
        if row["readiness"] == "MAPPED_RUNTIME_UNKNOWN"
        and row["overlap_class"] == "FULLY_CONTAINED"
    ]
    return {
        "inventory_rows": len(rows),
        "english_dialogue_owner_runs": len(owners),
        "overlap_summary": dict(sorted(summary.items())),
        "readiness_overlap_summary": dict(sorted(readiness_summary.items())),
        "fully_contained_runtime_candidates": patch_candidates,
        "rows": rows,
    }


def markdown(payload: dict[str, object]) -> str:
    summary = payload["overlap_summary"]
    readiness = payload["readiness_overlap_summary"]
    candidates = payload["fully_contained_runtime_candidates"]
    lines = [
        "# Pre-Pointer Dialogue Overlap Audit",
        "",
        f"- Inventory rows: `{payload['inventory_rows']}`.",
        f"- English dialogue owner runs: `{payload['english_dialogue_owner_runs']}`.",
        "- This audit classifies ownership only; it does not authorize a patch.",
        "",
        "## Ownership Classes",
        "",
        "| class | rows | meaning |",
        "| --- | ---: | --- |",
        f"| `FULLY_CONTAINED` | {summary.get('FULLY_CONTAINED', 0)} | The inventory byte range is inside one or more English dialogue runs. |",
        f"| `EDGE_OVERLAP` | {summary.get('EDGE_OVERLAP', 0)} | The row crosses a dialogue-run boundary, often a control byte or separator. |",
        f"| `RUN_INSIDE_ROW` | {summary.get('RUN_INSIDE_ROW', 0)} | The row is wider than the detected English run and needs boundary review. |",
        f"| `NO_OVERLAP` | {summary.get('NO_OVERLAP', 0)} | No English dialogue run was found at this ROM range. |",
        "",
        "## Readiness Breakdown",
        "",
        "| readiness / class | rows |",
        "| --- | ---: |",
    ]
    for key, count in readiness.items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Bounded Patch Candidates",
            "",
            f"The current safe subset contains `{len(candidates)}` rows: "
            + (", ".join(f"`{item}`" for item in candidates) if candidates else "none")
            + ".",
            "",
            "Rows with `FULLY_CONTAINED` ownership but missing Korean glyphs or translations remain blocked."
            " Rows with `EDGE_OVERLAP` or `RUN_INSIDE_ROW` must retain their control/separator skeleton."
            " No broad patch is authorized by this report alone.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    payload = audit(args.inventory, args.reference)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_markdown.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("inventory_rows", "english_dialogue_owner_runs", "overlap_summary", "fully_contained_runtime_candidates")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

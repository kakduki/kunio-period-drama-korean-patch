#!/usr/bin/env python3
"""Plan high-impact Hangul glyph batches beyond the current compact patch plan."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from rom_utils import REPO_ROOT


COVERAGE_JSON = REPO_ROOT / "rom_analysis" / "translation_glyph_coverage.json"
SLOT_PLAN_JSON = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "next_glyph_expansion_plan.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "next_glyph_expansion_plan.md"

PATCH_TILE_END = 0x1B5
BATCH_SIZES = [16, 32, 64, 96, 128, 160]


def planned_glyphs() -> set[str]:
    payload = json.loads(SLOT_PLAN_JSON.read_text(encoding="utf-8"))
    return {str(row["glyph"]) for row in payload["slots"]}


def row_score(row: dict[str, object]) -> tuple[int, int, str]:
    missing = row.get("missing_from_patch_plan", [])
    return (-len(missing), -int(row.get("hangul_count", 0)), str(row.get("source", "")))


def make_payload() -> dict[str, object]:
    coverage = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    current = planned_glyphs()
    rows = list(coverage["rows"])
    missing_counter = Counter()
    for row in rows:
        for glyph in row["missing_from_patch_plan"]:
            missing_counter[str(glyph)] += 1

    ranked = [
        {
            "glyph": glyph,
            "rows_needing_it": count,
        }
        for glyph, count in missing_counter.most_common()
    ]

    current_slot_count = len(current)
    available_extra_slots = max(0, PATCH_TILE_END - (0x101 + current_slot_count) + 1)
    simulations = []
    ranked_glyphs = [row["glyph"] for row in ranked]
    for requested in BATCH_SIZES:
        added = set(ranked_glyphs[: min(requested, available_extra_slots)])
        glyph_set = current | added
        ready_rows = [
            row
            for row in rows
            if set(row["unique_hangul"]).issubset(glyph_set)
        ]
        newly_ready = [
            row
            for row in ready_rows
            if not row["planned_patch_ready"]
        ]
        simulations.append(
            {
                "requested_extra_glyphs": requested,
                "extra_glyphs_used": len(added),
                "total_patch_glyphs": len(glyph_set),
                "rows_ready_total": len(ready_rows),
                "rows_newly_ready": len(newly_ready),
                "added_glyphs": list(ranked_glyphs[: min(requested, available_extra_slots)]),
                "example_newly_ready_rows": [
                    {
                        "source": row["source"],
                        "korean": row["korean"],
                        "category": row["category"],
                        "section": row["section"],
                        "length_delta": row["length_delta"],
                    }
                    for row in sorted(newly_ready, key=row_score)[:20]
                ],
            }
        )

    next_slots = []
    for index, glyph in enumerate(ranked_glyphs[:available_extra_slots], start=current_slot_count):
        tile = 0x101 + index
        if tile > PATCH_TILE_END:
            break
        next_slots.append(
            {
                "slot_index": index,
                "glyph": glyph,
                "tile": f"0x{tile:03X}",
                "prg_plus_0x7a_byte": f"0x{((tile - 0x7A) & 0xFF):02X}",
                "rows_needing_it": missing_counter[glyph],
            }
        )

    return {
        "source": str(COVERAGE_JSON.relative_to(REPO_ROOT)),
        "summary": {
            "current_patch_glyphs": current_slot_count,
            "available_extra_slots_in_current_bank_range": available_extra_slots,
            "ranked_missing_glyphs": len(ranked),
            "recommended_first_batch_size": min(32, available_extra_slots),
            "rule": "Rank glyphs by translation-row impact only; ROM offset safety is still a separate gate.",
        },
        "ranked_missing_glyphs": ranked,
        "next_slots": next_slots,
        "batch_simulations": simulations,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Next Glyph Expansion Plan",
        "",
        "This is a planning artifact for extending the compact Korean glyph set without running FCEUX autoplay.",
        "",
        "## Summary",
        "",
        f"- Current compact patch glyphs: **{summary['current_patch_glyphs']}**",
        f"- Extra slots still available in `0x101-0x1B5`: **{summary['available_extra_slots_in_current_bank_range']}**",
        f"- Ranked missing glyphs: **{summary['ranked_missing_glyphs']}**",
        f"- Recommended first batch: **{summary['recommended_first_batch_size']}** glyphs",
        "",
        "## Batch Simulation",
        "",
        "| extra glyphs | total glyphs | ready rows total | newly ready rows |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in payload["batch_simulations"]:
        lines.append(
            f"| {row['extra_glyphs_used']} | {row['total_patch_glyphs']} | "
            f"{row['rows_ready_total']} | {row['rows_newly_ready']} |"
        )

    lines += [
        "",
        "## First 32 Glyphs",
        "",
        "| # | glyph | tile | PRG byte (+0x7A) | rows needing it |",
        "| ---: | --- | --- | --- | ---: |",
    ]
    for row in payload["next_slots"][:32]:
        lines.append(
            f"| {row['slot_index']} | {row['glyph']} | `{row['tile']}` | "
            f"`{row['prg_plus_0x7a_byte']}` | {row['rows_needing_it']} |"
        )

    lines += [
        "",
        "## Rows Unlocked By First 32 Glyphs",
        "",
        "| section | category | source | korean | length delta |",
        "| --- | --- | --- | --- | ---: |",
    ]
    first_32 = next(
        row for row in payload["batch_simulations"] if row["requested_extra_glyphs"] == 32
    )
    examples = first_32["example_newly_ready_rows"]
    if examples:
        for row in examples:
            lines.append(
                f"| {row['section']} | {row['category']} | {row['source']} | "
                f"{row['korean']} | {row['length_delta']} |"
            )
    else:
        lines.append("| - | - | - | - | 0 |")

    lines += [
        "",
        "## Rule",
        "",
        "- This does not promote new ROM text patches by itself.",
        "- Use it to choose which Hangul glyphs to add before searching/promoting more translated offsets.",
        "- Text replacement still needs byte evidence, screen evidence, and length/padding safety.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    summary = payload["summary"]
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "current={current_patch_glyphs} extra_slots={available_extra_slots_in_current_bank_range} "
        "ranked_missing={ranked_missing_glyphs}".format(**summary)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

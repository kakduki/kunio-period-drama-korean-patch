#!/usr/bin/env python3
"""Plan scene-local Korean font pages for all pointer dialogue drafts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


POINTER_COUNT = 248
RUNTIME_PROVEN_SQUARE_SYLLABLE_CAPACITY = 17
PAGE_SYLLABLE_CAPACITY = 34
SOURCE_CODE_COUNT = 34
MMC3_EXTENDED_PAGE_BUDGET = 64
DEFAULT_DRAFT = REPO_ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "pointer_font_page_plan.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pointer_font_page_plan.md"


def hangul_syllables(text: str) -> set[str]:
    return {character for character in text if "\uac00" <= character <= "\ud7a3"}


def load_draft(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != POINTER_COUNT:
        raise ValueError(f"expected {POINTER_COUNT} rows, found {len(rows)}")
    if [int(row["pointer_index"]) for row in rows] != list(range(POINTER_COUNT)):
        raise ValueError("pointer indices must be 0..247 in order")
    return rows


def optimized_pages(
    records: list[tuple[int, set[str]]],
) -> tuple[list[dict[str, object]], list[int | None]]:
    """Pack non-adjacent records by shared syllables using best-fit decreasing."""

    bins: list[tuple[list[int], set[str]]] = []
    for pointer_index, syllables in sorted(
        records, key=lambda item: (-len(item[1]), item[0])
    ):
        choices = [
            (PAGE_SYLLABLE_CAPACITY - len(page_syllables | syllables), page_index)
            for page_index, (_, page_syllables) in enumerate(bins)
            if len(page_syllables | syllables) <= PAGE_SYLLABLE_CAPACITY
        ]
        if choices:
            _, page_index = min(choices)
            bins[page_index][0].append(pointer_index)
            bins[page_index][1].update(syllables)
        else:
            bins.append(([pointer_index], set(syllables)))

    assignments: list[int | None] = [None] * POINTER_COUNT
    pages: list[dict[str, object]] = []
    for page_index, (pointer_indices, syllables) in enumerate(bins):
        pointer_indices.sort()
        for pointer_index in pointer_indices:
            assignments[pointer_index] = page_index
        pages.append(
            {
                "page_index": page_index,
                "pointer_indices": pointer_indices,
                "record_count": len(pointer_indices),
                "syllable_count": len(syllables),
                "syllables": sorted(syllables),
            }
        )
    return pages, assignments


def build_plan(rows: list[dict[str, str]]) -> dict[str, object]:
    active = [
        row for row in rows if not row["translation_status"].startswith("excluded")
    ]
    oversize: list[dict[str, object]] = []
    packable: list[tuple[int, set[str]]] = []
    pages: list[dict[str, object]] = []
    current_rows: list[int] = []
    current_syllables: set[str] = set()

    def flush_page() -> None:
        nonlocal current_rows, current_syllables
        if not current_rows:
            return
        pages.append(
            {
                "page_index": len(pages),
                "pointer_indices": current_rows,
                "pointer_start": current_rows[0],
                "pointer_end": current_rows[-1],
                "record_count": len(current_rows),
                "syllable_count": len(current_syllables),
                "syllables": sorted(current_syllables),
            }
        )
        current_rows = []
        current_syllables = set()

    for row in active:
        pointer_index = int(row["pointer_index"])
        syllables = hangul_syllables(row["korean_text"])
        if len(syllables) > PAGE_SYLLABLE_CAPACITY:
            flush_page()
            oversize.append(
                {
                    "pointer_index": pointer_index,
                    "syllable_count": len(syllables),
                    "over_by": len(syllables) - PAGE_SYLLABLE_CAPACITY,
                    "korean_text": row["korean_text"],
                    "action": "shorten_translation_or_add_split_control",
                }
            )
            continue
        packable.append((pointer_index, syllables))
        if current_rows and len(current_syllables | syllables) > PAGE_SYLLABLE_CAPACITY:
            flush_page()
        current_rows.append(pointer_index)
        current_syllables.update(syllables)
    flush_page()

    assigned = sum(page["record_count"] for page in pages)
    packed_pages, page_assignments = optimized_pages(packable)
    status = (
        "READY_WITH_TEXT_REVISIONS"
        if oversize
        else "READY_FOR_8X16_PAGE_COMPILATION"
    )
    return {
        "status": status,
        "policy": {
            "renderer": "one_source_code_per_8x16_korean_syllable",
            "page_syllable_capacity": PAGE_SYLLABLE_CAPACITY,
            "previous_square_16x16_capacity": RUNTIME_PROVEN_SQUARE_SYLLABLE_CAPACITY,
            "source_code_range": "34 renderer-owned codes; exact per-page allocator remains explicit",
            "source_code_count": SOURCE_CODE_COUNT,
            "font_profile_gate": "PTR181_8X16_SEMANTIC_RUNTIME_PASS",
            "page_switch_scope": "scene_or_record-range lifecycle required",
            "english_reference_role": "pointer ownership and control structure only",
        },
        "coverage": {
            "draft_rows": len(rows),
            "active_rows": len(active),
            "excluded_rows": len(rows) - len(active),
            "assigned_rows": assigned,
            "oversize_rows": len(oversize),
            "unique_hangul_syllables": len(
                set().union(*(hangul_syllables(row["korean_text"]) for row in active))
            ),
            "planned_pages": len(pages),
            "optimized_pages": len(packed_pages),
            "optimized_page_capacity_limit": MMC3_EXTENDED_PAGE_BUDGET,
            "optimized_pages_with_one_reserved_per_oversize": len(packed_pages)
            + len(oversize),
            "fits_mmc3_extended_chr_page_budget": len(packed_pages) + len(oversize)
            <= MMC3_EXTENDED_PAGE_BUDGET,
        },
        "sequential_pages": pages,
        "optimized_pages": packed_pages,
        "pointer_page_assignments": page_assignments,
        "oversize_records": oversize,
    }


def render_markdown(payload: dict[str, object]) -> str:
    coverage = payload["coverage"]
    pages = payload["optimized_pages"]
    oversize = payload["oversize_records"]
    assert isinstance(coverage, dict)
    assert isinstance(pages, list)
    assert isinstance(oversize, list)
    lines = [
        "# Pointer Font Page Plan",
        "",
        f"Status: **{payload['status']}**",
        "",
        "The English patch supplies pointer ownership and control structure. Korean",
        "glyph pages use the scene-scoped 8x16 renderer proven by PTR-181.",
        "",
        f"- Active records: `{coverage['active_rows']}`",
        f"- Assigned records: `{coverage['assigned_rows']}`",
        f"- Sequential {PAGE_SYLLABLE_CAPACITY}-syllable pages: `{coverage['planned_pages']}`",
        f"- Optimized shared pages: `{coverage['optimized_pages']}`",
        f"- Upper bound after reserving one page per oversize record: `{coverage['optimized_pages_with_one_reserved_per_oversize']}` / `{coverage['optimized_page_capacity_limit']}`",
        f"- Fits extended MMC3 CHR page budget: `{coverage['fits_mmc3_extended_chr_page_budget']}`",
        "- Selected profile: one source code per 8x16 Korean syllable; PTR-181 semantic text and 7200-frame restoration passed.",
        f"- Unique Hangul syllables: `{coverage['unique_hangul_syllables']}`",
        f"- Records requiring wording revision or a split: `{coverage['oversize_rows']}`",
        "",
        "## Pages",
        "",
        "| page | pointers | records | syllables |",
        "| ---: | --- | ---: | ---: |",
    ]
    for page in pages:
        lines.append(
            f"| {page['page_index']} | `{','.join(str(value) for value in page['pointer_indices'])}` | "
            f"{page['record_count']} | {page['syllable_count']} |"
        )
    lines += [
        "",
        "## Text Revisions",
        "",
        "| pointer | syllables | over | Korean draft |",
        "| ---: | ---: | ---: | --- |",
    ]
    for record in oversize:
        lines.append(
            f"| {record['pointer_index']} | {record['syllable_count']} | "
            f"{record['over_by']} | {record['korean_text']} |"
        )
    lines += [
        "",
        "A page assignment is a build input, not runtime proof. Each page still needs",
        "a bounded mapper lifecycle test before promotion.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = build_plan(load_draft(args.draft))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(
        f"status={payload['status']} "
        f"sequential_pages={payload['coverage']['planned_pages']} "
        f"optimized_pages={payload['coverage']['optimized_pages']} "
        f"oversize={payload['coverage']['oversize_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

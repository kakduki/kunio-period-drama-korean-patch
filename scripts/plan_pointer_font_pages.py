#!/usr/bin/env python3
"""Plan scene-local Korean font pages for all pointer dialogue drafts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


POINTER_COUNT = 248
PAGE_SYLLABLE_CAPACITY = 17
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


def build_plan(rows: list[dict[str, str]]) -> dict[str, object]:
    active = [
        row for row in rows if not row["translation_status"].startswith("excluded")
    ]
    oversize: list[dict[str, object]] = []
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
        if current_rows and len(current_syllables | syllables) > PAGE_SYLLABLE_CAPACITY:
            flush_page()
        current_rows.append(pointer_index)
        current_syllables.update(syllables)
    flush_page()

    assigned = sum(page["record_count"] for page in pages)
    status = "READY_WITH_TEXT_REVISIONS" if oversize else "READY_FOR_PAGE_COMPILATION"
    return {
        "status": status,
        "policy": {
            "renderer": "paired_8x16_cells_for_16x16_korean",
            "page_syllable_capacity": PAGE_SYLLABLE_CAPACITY,
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
        },
        "pages": pages,
        "oversize_records": oversize,
    }


def render_markdown(payload: dict[str, object]) -> str:
    coverage = payload["coverage"]
    pages = payload["pages"]
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
        "glyph pages are planned independently for the proven paired-cell renderer.",
        "",
        f"- Active records: `{coverage['active_rows']}`",
        f"- Assigned records: `{coverage['assigned_rows']}`",
        f"- Planned 17-syllable pages: `{coverage['planned_pages']}`",
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
            f"| {page['page_index']} | `{page['pointer_start']}-{page['pointer_end']}` | "
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
        f"pages={payload['coverage']['planned_pages']} "
        f"oversize={payload['coverage']['oversize_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

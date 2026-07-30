#!/usr/bin/env python3
"""Compare the English font footprint with full Korean script requirements."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from generate_translation_glyph_coverage import parse_translation_rows, row_hangul
from rom_utils import REPO_ROOT


ENGLISH_FONT_MAP = REPO_ROOT / "rom_analysis" / "english_font_slot_map.json"
PROVEN_TIER2 = (
    REPO_ROOT
    / "text_data"
    / "korean_scene_batches"
    / "opening_ptr_182_16x16_capacity_tier2.json"
)
OUT_JSON = REPO_ROOT / "rom_analysis" / "full_script_font_capacity.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "full_script_font_capacity.md"
TILES_PER_KOREAN_SYLLABLE = 4
SOURCE_CODES_PER_KOREAN_SYLLABLE = 2


def load_english_bank7_changed_tiles() -> int:
    payload = json.loads(ENGLISH_FONT_MAP.read_text(encoding="utf-8"))
    for bank in payload["changed_chr_banks"]:
        if int(bank["chr_bank"]) == 7:
            return int(bank["changed_tile_count"])
    raise ValueError("English reference has no CHR Bank 7 record")


def load_proven_glyph_capacity() -> tuple[int, int]:
    payload = json.loads(PROVEN_TIER2.read_text(encoding="utf-8"))
    pairs = payload["capacity_profile"]["glyph_code_pairs"]
    source_codes = {code for pair in pairs.values() for code in pair}
    if len(source_codes) != len(pairs) * SOURCE_CODES_PER_KOREAN_SYLLABLE:
        raise ValueError("proven Tier-2 glyph pairs reuse a source code")
    return len(pairs), len(source_codes)


def pack_rows(rows: list[dict[str, str]], capacity: int) -> dict[str, object]:
    prepared = []
    oversize = []
    for index, row in enumerate(rows):
        glyphs = set(row_hangul(row))
        item = {
            "row_index": index,
            "section": row["section"],
            "category": row["category"],
            "source": row["source"],
            "korean": row["korean"],
            "glyphs": sorted(glyphs),
            "unique_glyph_count": len(glyphs),
        }
        if len(glyphs) > capacity:
            oversize.append(item)
        else:
            prepared.append(item)

    prepared.sort(key=lambda item: (-item["unique_glyph_count"], item["section"], item["source"]))
    pages: list[dict[str, object]] = []
    for item in prepared:
        item_glyphs = set(item["glyphs"])
        choices = []
        for page_index, page in enumerate(pages):
            merged = set(page["glyphs"]) | item_glyphs
            if len(merged) <= capacity:
                choices.append((len(merged) - len(page["glyphs"]), len(merged), page_index, merged))
        if choices:
            _, _, page_index, merged = min(choices)
            page = pages[page_index]
            page["glyphs"] = sorted(merged)
            page["rows"].append(item)
        else:
            pages.append({"glyphs": sorted(item_glyphs), "rows": [item]})

    for index, page in enumerate(pages):
        page["page_index"] = index
        page["unique_glyph_count"] = len(page["glyphs"])
        page["row_count"] = len(page["rows"])
    return {"capacity": capacity, "page_count": len(pages), "oversize_rows": oversize, "pages": pages}


def make_payload() -> dict[str, object]:
    rows = parse_translation_rows()
    all_glyphs = {glyph for row in rows for glyph in row_hangul(row)}
    frequency = Counter(glyph for row in rows for glyph in row_hangul(row))
    english_changed_tiles = load_english_bank7_changed_tiles()
    proven_glyphs, proven_source_codes = load_proven_glyph_capacity()
    theoretical_glyphs = english_changed_tiles // TILES_PER_KOREAN_SYLLABLE

    section_glyphs: dict[str, set[str]] = defaultdict(set)
    section_rows: Counter[str] = Counter()
    for row in rows:
        section_glyphs[row["section"]].update(row_hangul(row))
        section_rows[row["section"]] += 1

    section_report = [
        {
            "section": section,
            "row_count": section_rows[section],
            "unique_glyph_count": len(glyphs),
            "minimum_proven_pages": math.ceil(len(glyphs) / proven_glyphs) if glyphs else 0,
            "minimum_theoretical_pages": math.ceil(len(glyphs) / theoretical_glyphs) if glyphs else 0,
        }
        for section, glyphs in section_glyphs.items()
    ]
    section_report.sort(key=lambda item: (-item["unique_glyph_count"], item["section"]))

    return {
        "inputs": {
            "translation_rows": len(rows),
            "unique_hangul": len(all_glyphs),
            "english_bank7_changed_tiles": english_changed_tiles,
            "tiles_per_korean_syllable": TILES_PER_KOREAN_SYLLABLE,
            "source_codes_per_korean_syllable": SOURCE_CODES_PER_KOREAN_SYLLABLE,
            "proven_source_codes_per_page": proven_source_codes,
        },
        "capacity": {
            "proven_syllables_per_page": proven_glyphs,
            "theoretical_syllables_from_english_changed_tiles": theoretical_glyphs,
            "minimum_pages_by_unique_count_proven": math.ceil(len(all_glyphs) / proven_glyphs),
            "minimum_pages_by_unique_count_theoretical": math.ceil(len(all_glyphs) / theoretical_glyphs),
        },
        "top_hangul": frequency.most_common(40),
        "sections": section_report,
        "proven_page_pack": pack_rows(rows, proven_glyphs),
        "theoretical_page_pack": pack_rows(rows, theoretical_glyphs),
    }


def write_markdown(payload: dict[str, object]) -> None:
    inputs = payload["inputs"]
    capacity = payload["capacity"]
    proven = payload["proven_page_pack"]
    theoretical = payload["theoretical_page_pack"]
    lines = [
        "# Full Script Font Capacity",
        "",
        "This report applies the English patch's CHR footprint to the current",
        "Korean 16x16 renderer instead of treating one English tile as one Korean syllable.",
        "",
        "## Capacity",
        "",
        f"- Translation rows: **{inputs['translation_rows']}**",
        f"- Unique Hangul syllables: **{inputs['unique_hangul']}**",
        f"- English reference Bank 7 changed tiles: **{inputs['english_bank7_changed_tiles']}**",
        f"- Korean 16x16 cost: **{inputs['tiles_per_korean_syllable']} CHR tiles / {inputs['source_codes_per_korean_syllable']} source codes per syllable**",
        f"- Runtime-proven page: **{capacity['proven_syllables_per_page']} syllables / {inputs['proven_source_codes_per_page']} source codes**",
        f"- English-footprint theoretical page ceiling: **{capacity['theoretical_syllables_from_english_changed_tiles']} syllables**",
        f"- Absolute minimum pages at proven capacity: **{capacity['minimum_pages_by_unique_count_proven']}**",
        f"- Absolute minimum pages at theoretical tile capacity: **{capacity['minimum_pages_by_unique_count_theoretical']}**",
        "",
        "The English patch can keep one alphabet page because letters are reused globally.",
        "The Korean patch cannot perform a direct byte-for-byte alphabet substitution:",
        "the current script needs scene/page ownership or a different renderer encoding.",
        "",
        "## Packing Simulation",
        "",
        "| model | capacity | packed pages | rows too large for one page |",
        "| --- | ---: | ---: | ---: |",
        f"| runtime-proven | {proven['capacity']} | {proven['page_count']} | {len(proven['oversize_rows'])} |",
        f"| English-tile theoretical | {theoretical['capacity']} | {theoretical['page_count']} | {len(theoretical['oversize_rows'])} |",
        "",
        "The packing result is a lower-bound planning model. Runtime scene grouping,",
        "control bytes, menus, and mapper lifetime can only increase the required pages.",
        "",
        "## Section Demand",
        "",
        "| section | rows | unique Hangul | proven pages minimum | theoretical pages minimum |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for section in payload["sections"]:
        lines.append(
            f"| {section['section']} | {section['row_count']} | {section['unique_glyph_count']} | "
            f"{section['minimum_proven_pages']} | {section['minimum_theoretical_pages']} |"
        )
    if proven["oversize_rows"]:
        lines += [
            "",
            "## Rows Exceeding The Proven Page",
            "",
            "| section | Korean | unique Hangul |",
            "| --- | --- | ---: |",
        ]
        for row in proven["oversize_rows"]:
            lines.append(f"| {row['section']} | {row['korean']} | {row['unique_glyph_count']} |")
    lines += [
        "",
        "## Decision",
        "",
        "- Reuse the English 248-entry pointer relocation model for text ownership and record packing.",
        "- Do not reuse the English one-page alphabet assumption for Korean glyph storage.",
        "- The next compiler input must assign every translated record to a declared font page.",
        "- A page can be promoted only after its mapper activation and restore boundary pass runtime checks.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"wrote={OUT_JSON}")
    print(f"wrote={OUT_MD}")
    print(
        "unique_hangul={unique} proven_capacity={proven} proven_pages={pages} oversize_rows={oversize}".format(
            unique=payload["inputs"]["unique_hangul"],
            proven=payload["capacity"]["proven_syllables_per_page"],
            pages=payload["proven_page_pack"]["page_count"],
            oversize=len(payload["proven_page_pack"]["oversize_rows"]),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

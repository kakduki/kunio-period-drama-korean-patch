#!/usr/bin/env python3
"""Measure Hangul glyph coverage for the current translation data and patch plan."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from rom_utils import REPO_ROOT


TRANSLATION_DATA = REPO_ROOT / "text_data" / "translation_data.txt"
SLOT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "translation_glyph_coverage.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "translation_glyph_coverage.md"


def is_hangul(ch: str) -> bool:
    return "\uac00" <= ch <= "\ud7a3"


def parse_translation_rows() -> list[dict[str, str]]:
    rows = []
    current_section = ""
    for raw in TRANSLATION_DATA.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            current_section = line.lstrip("#").strip(" =")
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 2:
            continue
        rows.append(
            {
                "source": parts[0],
                "korean": parts[1],
                "category": parts[2] if len(parts) > 2 else "",
                "note": parts[3] if len(parts) > 3 else "",
                "section": current_section,
            }
        )
    return rows


def load_current_char_map() -> set[str]:
    payload = json.loads(CHAR_MAP.read_text(encoding="utf-8"))
    return set(payload.get("sorted", []))


def load_planned_glyphs() -> set[str]:
    payload = json.loads(SLOT_PLAN.read_text(encoding="utf-8"))
    return {str(row["glyph"]) for row in payload["slots"]}


def row_hangul(row: dict[str, str]) -> list[str]:
    return [ch for ch in row["korean"] if is_hangul(ch)]


def make_payload() -> dict[str, object]:
    rows = parse_translation_rows()
    current_chars = load_current_char_map()
    planned_glyphs = load_planned_glyphs()
    all_hangul = Counter(ch for row in rows for ch in row_hangul(row))
    current_patch_covered = set(all_hangul) & planned_glyphs
    char_map_covered = set(all_hangul) & current_chars

    row_reports = []
    for row in rows:
        glyphs = row_hangul(row)
        unique = sorted(set(glyphs))
        missing_from_plan = [ch for ch in unique if ch not in planned_glyphs]
        missing_from_char_map = [ch for ch in unique if ch not in current_chars]
        row_reports.append(
            {
                **row,
                "hangul_count": len(glyphs),
                "unique_hangul": unique,
                "planned_patch_ready": not missing_from_plan,
                "missing_from_patch_plan": missing_from_plan,
                "char_map_ready": not missing_from_char_map,
                "missing_from_char_map": missing_from_char_map,
                "korean_length": len(row["korean"]),
                "source_length": len(row["source"]),
                "length_delta": len(row["korean"]) - len(row["source"]),
            }
        )

    missing_plan_counter = Counter(
        ch
        for row in row_reports
        for ch in row["missing_from_patch_plan"]
    )
    missing_char_map_counter = Counter(
        ch
        for row in row_reports
        for ch in row["missing_from_char_map"]
    )

    return {
        "source": str(TRANSLATION_DATA.relative_to(REPO_ROOT)),
        "summary": {
            "translation_rows": len(rows),
            "unique_hangul_total": len(all_hangul),
            "patch_plan_glyphs": len(planned_glyphs),
            "unique_hangul_in_patch_plan": len(current_patch_covered),
            "unique_hangul_missing_from_patch_plan": len(set(all_hangul) - planned_glyphs),
            "unique_hangul_in_char_map": len(char_map_covered),
            "unique_hangul_missing_from_char_map": len(set(all_hangul) - current_chars),
            "rows_ready_for_current_patch_plan": sum(1 for row in row_reports if row["planned_patch_ready"]),
            "rows_ready_for_char_map": sum(1 for row in row_reports if row["char_map_ready"]),
        },
        "top_translation_hangul": all_hangul.most_common(40),
        "top_missing_from_patch_plan": missing_plan_counter.most_common(40),
        "top_missing_from_char_map": missing_char_map_counter.most_common(40),
        "rows": row_reports,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Translation Glyph Coverage",
        "",
        "This report compares the full `translation_data.txt` Hangul set with the current compact Bank 1 patch glyph plan.",
        "",
        "## Summary",
        "",
        f"- Translation rows: **{summary['translation_rows']}**",
        f"- Unique Hangul in translations: **{summary['unique_hangul_total']}**",
        f"- Current patch-plan glyphs: **{summary['patch_plan_glyphs']}**",
        f"- Unique Hangul already in patch plan: **{summary['unique_hangul_in_patch_plan']}**",
        f"- Unique Hangul missing from patch plan: **{summary['unique_hangul_missing_from_patch_plan']}**",
        f"- Rows fully covered by current patch plan: **{summary['rows_ready_for_current_patch_plan']}**",
        f"- Rows fully covered by current char_map: **{summary['rows_ready_for_char_map']}**",
        "",
        "## Most Common Missing Glyphs From Patch Plan",
        "",
        "| glyph | rows needing it |",
        "| --- | ---: |",
    ]
    for glyph, count in payload["top_missing_from_patch_plan"][:30]:
        lines.append(f"| {glyph} | {count} |")
    if not payload["top_missing_from_patch_plan"]:
        lines.append("| - | 0 |")

    lines += [
        "",
        "## Fully Covered Rows",
        "",
        "| section | category | source | korean | length delta |",
        "| --- | --- | --- | --- | ---: |",
    ]
    ready_rows = [row for row in payload["rows"] if row["planned_patch_ready"]]
    for row in ready_rows[:60]:
        lines.append(
            f"| {row['section']} | {row['category']} | {row['source']} | "
            f"{row['korean']} | {row['length_delta']} |"
        )
    if not ready_rows:
        lines.append("| - | - | - | - | 0 |")

    lines += [
        "",
        "## Highest-Impact Rows Still Missing Glyphs",
        "",
        "| section | category | source | korean | missing glyphs |",
        "| --- | --- | --- | --- | --- |",
    ]
    missing_rows = [
        row
        for row in payload["rows"]
        if row["missing_from_patch_plan"]
    ]
    missing_rows.sort(key=lambda row: (-row["hangul_count"], row["section"], row["source"]))
    for row in missing_rows[:60]:
        lines.append(
            f"| {row['section']} | {row['category']} | {row['source']} | "
            f"{row['korean']} | {''.join(row['missing_from_patch_plan'])} |"
        )

    lines += [
        "",
        "## Rule",
        "",
        "- This is a font/encoding planning report only. A row being glyph-covered does not mean its ROM offset is known or safe to patch.",
        "- Promotion to an IPS candidate still requires ROM byte evidence, runtime/screen evidence, and length/padding safety.",
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
        "rows={translation_rows} unique_hangul={unique_hangul_total} "
        "patch_ready_rows={rows_ready_for_current_patch_plan}".format(**summary)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

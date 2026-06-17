#!/usr/bin/env python3
"""Report which planned glyph-expansion batches are buildable with current font assets."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


EXPANSION_PLAN = REPO_ROOT / "rom_analysis" / "next_glyph_expansion_plan.json"
CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
FONT_BIN = REPO_ROOT / "font" / "korean_font_8x16.bin"
OUT_JSON = REPO_ROOT / "rom_analysis" / "font_expansion_readiness.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "font_expansion_readiness.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_payload() -> dict[str, object]:
    expansion = load_json(EXPANSION_PLAN)
    char_map = load_json(CHAR_MAP)
    available = set(str(ch) for ch in char_map.get("sorted", []))
    font_size = FONT_BIN.stat().st_size if FONT_BIN.exists() else 0
    expected_font_size = len(available) * 32
    next_slots = list(expansion["next_slots"])
    batch_rows = []
    max_prefix_buildable = 0
    for index, slot in enumerate(next_slots, start=1):
        if str(slot["glyph"]) in available:
            max_prefix_buildable = index
        else:
            break

    for sim in expansion["batch_simulations"]:
        requested = int(sim["requested_extra_glyphs"])
        slots = next_slots[:requested]
        missing = [slot for slot in slots if str(slot["glyph"]) not in available]
        batch_rows.append(
            {
                "requested_extra_glyphs": requested,
                "total_patch_glyphs": sim["total_patch_glyphs"],
                "rows_ready_total": sim["rows_ready_total"],
                "rows_newly_ready": sim["rows_newly_ready"],
                "buildable_with_current_font_assets": not missing,
                "missing_glyph_count": len(missing),
                "first_missing_glyph": str(missing[0]["glyph"]) if missing else "",
                "first_missing_slot": missing[0]["tile"] if missing else "",
                "missing_glyphs": [
                    {
                        "glyph": str(slot["glyph"]),
                        "tile": slot["tile"],
                        "prg_plus_0x7a_byte": slot["prg_plus_0x7a_byte"],
                        "rows_needing_it": slot["rows_needing_it"],
                    }
                    for slot in missing[:40]
                ],
            }
        )

    return {
        "source": {
            "expansion_plan": str(EXPANSION_PLAN.relative_to(REPO_ROOT)),
            "char_map": str(CHAR_MAP.relative_to(REPO_ROOT)),
            "font_bin": str(FONT_BIN.relative_to(REPO_ROOT)),
        },
        "summary": {
            "char_map_entries": len(available),
            "font_bin_bytes": font_size,
            "expected_font_bin_bytes": expected_font_size,
            "font_bin_matches_char_map": font_size >= expected_font_size,
            "planned_extra_slots": len(next_slots),
            "max_prefix_buildable_extra_glyphs": max_prefix_buildable,
            "rule": "Buildability here only means glyph bitmap data exists; text promotion still needs ROM/runtime/screen proof.",
        },
        "batches": batch_rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Font Expansion Readiness",
        "",
        "This report checks whether the planned glyph batches can be built from the current `font/char_map.json` and `font/korean_font_8x16.bin` assets.",
        "",
        "## Summary",
        "",
        f"- char_map entries: **{summary['char_map_entries']}**",
        f"- font binary bytes: **{summary['font_bin_bytes']}**",
        f"- expected bytes from char_map: **{summary['expected_font_bin_bytes']}**",
        f"- font binary covers char_map: **{str(summary['font_bin_matches_char_map']).lower()}**",
        f"- planned extra slots: **{summary['planned_extra_slots']}**",
        f"- max prefix buildable extra glyphs: **{summary['max_prefix_buildable_extra_glyphs']}**",
        "",
        "## Batch Readiness",
        "",
        "| extra glyphs | rows ready total | newly ready rows | buildable now | missing glyphs | first missing | first missing tile |",
        "| ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for row in payload["batches"]:
        lines.append(
            f"| {row['requested_extra_glyphs']} | {row['rows_ready_total']} | "
            f"{row['rows_newly_ready']} | {str(row['buildable_with_current_font_assets']).lower()} | "
            f"{row['missing_glyph_count']} | {row['first_missing_glyph'] or '-'} | "
            f"{row['first_missing_slot'] or '-'} |"
        )

    blocked = [row for row in payload["batches"] if row["missing_glyphs"]]
    if blocked:
        first = blocked[0]
        lines += [
            "",
            f"## First Blocked Batch: {first['requested_extra_glyphs']} Extra Glyphs",
            "",
            "| glyph | tile | PRG byte (+0x7A) | rows needing it |",
            "| --- | --- | --- | ---: |",
        ]
        for row in first["missing_glyphs"]:
            lines.append(
                f"| {row['glyph']} | `{row['tile']}` | `{row['prg_plus_0x7a_byte']}` | "
                f"{row['rows_needing_it']} |"
            )

    lines += [
        "",
        "## Rule",
        "",
        "- This does not promote any new text into the IPS.",
        "- If a batch is blocked here, regenerate or extend font assets before building that glyph batch.",
        "- Even when a glyph batch is buildable, ROM text replacement still needs byte evidence, runtime/screen evidence, and length/padding safety.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "max_buildable={max_prefix_buildable_extra_glyphs} char_map={char_map_entries}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

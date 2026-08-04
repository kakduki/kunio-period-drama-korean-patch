#!/usr/bin/env python3
"""Generate a narrow boss-dialogue target list from structural references."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_ENGLISH = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_DRAFT = REPO_ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv"
DEFAULT_CSV = REPO_ROOT / "rom_analysis" / "boss_dialogue_targets.csv"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "boss_dialogue_targets.md"

FIELDS = [
    "pointer_index",
    "pointer_rom_offset",
    "english_pointer_cpu",
    "english_record_rom_offset",
    "korean_text",
    "trigger_term",
    "natural_route_status",
    "evidence_scope",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_rows(english_path: Path, draft_path: Path) -> list[dict[str, str]]:
    drafts = {
        int(row["pointer_index"]): row
        for row in read_tsv(draft_path)
        if row.get("pointer_index", "").isdigit()
    }
    rows: list[dict[str, str]] = []
    for row in read_tsv(english_path):
        if row.get("record_kind") != "pointer_pair":
            continue
        if "BOSS" not in row.get("en_text", "").upper():
            continue
        index = int(row["pointer_index"])
        rows.append(
            {
                "pointer_index": f"{index:03d}",
                "pointer_rom_offset": row.get("pointer_rom_offset", ""),
                "english_pointer_cpu": row.get("en_pointer_cpu", ""),
                "english_record_rom_offset": row.get("en_rom_offset", ""),
                "korean_text": drafts.get(index, {}).get("korean_text", ""),
                "trigger_term": "BOSS",
                "natural_route_status": "UNKNOWN",
                "evidence_scope": "Structural target only; natural event and screen proof remain open.",
            }
        )
    return rows


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Boss Dialogue Targets",
        "",
        "This queue is derived from the structural English-reference dump and the Korean draft.",
        "It identifies likely boss-related pointer records without redistributing the reference script.",
        "",
        f"- Target records: **{len(rows)}**",
        "- Natural route status: **UNKNOWN** for every row",
        "- Release rule: a forced pointer render is not natural event proof",
        "",
        "| pointer | pointer ROM | CPU | record ROM | Korean draft | status |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        korean = row["korean_text"].replace("|", "\\|")
        lines.append(
            f"| {row['pointer_index']} | `{row['pointer_rom_offset']}` | `{row['english_pointer_cpu']}` | "
            f"`{row['english_record_rom_offset']}` | {korean} | {row['natural_route_status']} |"
        )
    lines += [
        "",
        "## Next Capture Rule",
        "",
        "Use these records to classify a screen only after the route reaches the corresponding event naturally.",
        "Do not promote a row from UNKNOWN using a forced pointer write alone.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english", type=Path, default=DEFAULT_ENGLISH)
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--csv-out", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    rows = build_rows(args.english, args.draft)
    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    write_markdown(args.markdown_out, rows)
    print(f"Wrote {args.csv_out}")
    print(f"Wrote {args.markdown_out}")
    print(f"target_count={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

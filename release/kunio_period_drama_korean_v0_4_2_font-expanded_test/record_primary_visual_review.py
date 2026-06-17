#!/usr/bin/env python3
"""Record visual review for a row already applied in the primary patch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_primary_visual_checklist import PRIMARY_CONTENTS_JSON, normalize_rom, screen_hint
from readable_labels import readable_for_romaji
from rom_utils import REPO_ROOT


DEFAULT_REVIEW = REPO_ROOT / "rom_analysis" / "primary_visual_review.json"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def review_template() -> dict[str, object]:
    contents = load_json(PRIMARY_CONTENTS_JSON)
    rows = []
    for row in contents.get("applied_rows", []):
        if not isinstance(row, dict):
            continue
        readable = readable_for_romaji(row.get("romaji", ""))
        rows.append(
            {
                "rom_hit": normalize_rom(row.get("rom_hit")),
                "romaji": row.get("romaji", ""),
                "meaning": row.get("meaning", ""),
                "source_display": readable.get("source_display") or row.get("source_display", ""),
                "korean_display": readable.get("korean_display") or row.get("korean_display", ""),
                "screen_hint": screen_hint(row),
                "visual_context_confirmed": False,
                "screen_context": "",
                "reviewer_note": "",
            }
        )
    rows.sort(key=lambda item: str(item["rom_hit"]))
    return {
        "source": str(PRIMARY_CONTENTS_JSON.relative_to(REPO_ROOT)),
        "rule": "Only confirm rows after the patched ROM visibly shows the intended Korean text in the expected screen context.",
        "rows": rows,
    }


def ensure_review(path: Path) -> dict[str, object]:
    template = review_template()
    current = load_json(path)
    existing = {
        normalize_rom(row.get("rom_hit")): row
        for row in current.get("rows", [])
        if isinstance(row, dict)
    }
    for row in template["rows"]:
        saved = existing.get(normalize_rom(row.get("rom_hit")))
        if not saved:
            continue
        row["visual_context_confirmed"] = bool(saved.get("visual_context_confirmed", False))
        row["screen_context"] = saved.get("screen_context", "")
        row["reviewer_note"] = saved.get("reviewer_note", "")
    write_json(path, template)
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom_offset", help="ROM offset to mark, for example 0x07227.")
    parser.add_argument("--screen-context", default="", help="Short description of the visible screen.")
    parser.add_argument("--note", default="", help="Optional reviewer note.")
    parser.add_argument("--confirm", action="store_true", help="Set visual_context_confirmed=true.")
    parser.add_argument("--clear", action="store_true", help="Set visual_context_confirmed=false.")
    parser.add_argument("--visual-review", default=str(DEFAULT_REVIEW))
    args = parser.parse_args()

    if args.confirm == args.clear:
        print("ERROR: pass exactly one of --confirm or --clear.")
        return 1

    review_path = Path(args.visual_review).expanduser()
    if not review_path.is_absolute():
        review_path = REPO_ROOT / review_path
    rom = normalize_rom(args.rom_offset)
    review = ensure_review(review_path.resolve())

    found = False
    for row in review["rows"]:
        if not isinstance(row, dict) or normalize_rom(row.get("rom_hit")) != rom:
            continue
        found = True
        row["visual_context_confirmed"] = bool(args.confirm)
        row["screen_context"] = args.screen_context
        row["reviewer_note"] = args.note
        break

    if not found:
        print(f"ERROR: ROM offset {rom} is not an applied primary patch row.")
        return 1

    write_json(review_path, review)
    print(f"updated={review_path}")
    print(f"rom_offset={rom}")
    print(f"visual_context_confirmed={args.confirm}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

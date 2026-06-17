#!/usr/bin/env python3
"""Record visual-context review for a broad-scan proof row."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_v043_from_broad_scan_proof import (
    DEFAULT_PROOF_PACKET,
    DEFAULT_REVIEW,
    DEFAULT_SUMMARY,
    normalize_rom,
    write_review_template,
)
from readable_labels import readable_for_romaji
from rom_utils import REPO_ROOT


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summary_matches(path: Path) -> set[str]:
    summary = load_json(path)
    matches = set()
    for row in summary.get("promotable_after_visual_review", []):
        if isinstance(row, dict) and row.get("rom_offset"):
            matches.add(normalize_rom(row["rom_offset"]))
    return matches


def ensure_review(path: Path) -> dict[str, object]:
    proof_packet = load_json(DEFAULT_PROOF_PACKET)
    write_review_template(path, proof_packet)
    return load_json(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom_offset", help="ROM offset to mark, for example 0x0440C.")
    parser.add_argument("--screen-context", default="", help="Short description of the visible screen.")
    parser.add_argument("--note", default="", help="Optional reviewer note.")
    parser.add_argument("--confirm", action="store_true", help="Set visual_context_confirmed=true.")
    parser.add_argument("--clear", action="store_true", help="Set visual_context_confirmed=false.")
    parser.add_argument("--visual-review", default=str(DEFAULT_REVIEW))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    args = parser.parse_args()

    if args.confirm == args.clear:
        print("ERROR: pass exactly one of --confirm or --clear.")
        return 1

    rom = normalize_rom(args.rom_offset)
    review_path = Path(args.visual_review).expanduser()
    if not review_path.is_absolute():
        review_path = REPO_ROOT / review_path
    summary_path = Path(args.summary).expanduser()
    if not summary_path.is_absolute():
        summary_path = REPO_ROOT / summary_path

    review = ensure_review(review_path.resolve())
    matches = summary_matches(summary_path.resolve())

    found = False
    for row in review.get("rows", []):
        if not isinstance(row, dict) or normalize_rom(row.get("rom_offset")) != rom:
            continue
        found = True
        row["visual_context_confirmed"] = bool(args.confirm)
        row["screen_context"] = args.screen_context
        row["reviewer_note"] = args.note
        readable = readable_for_romaji(row.get("romaji", ""))
        for key, value in readable.items():
            row[key] = value
        row["cpu_read_match_present"] = rom in matches
        if args.confirm and rom not in matches:
            row["review_warning"] = "visual context marked true, but broad-scan summary has no CPU read match yet"
        else:
            row.pop("review_warning", None)
        break

    if not found:
        print(f"ERROR: ROM offset {rom} is not in {review_path}")
        return 1

    write_json(review_path, review)
    print(f"updated={review_path}")
    print(f"rom_offset={rom}")
    print(f"visual_context_confirmed={args.confirm}")
    print(f"cpu_read_match_present={rom in matches}")
    if args.confirm and rom not in matches:
        print("WARNING: visual context is true, but v0.4.3 still will not build until CPU-read proof exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

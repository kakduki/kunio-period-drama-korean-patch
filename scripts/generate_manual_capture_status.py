#!/usr/bin/env python3
"""Summarize which manual FCEUX capture cards have screen-dump evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


CARDS_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_cards.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_status.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "manual_capture_status.md"


def normalize_rom_hit(value: object) -> str:
    text = str(value or "").replace("ROM+", "").strip()
    if text.lower().startswith("0x"):
        return f"0x{int(text, 16):05X}"
    return text


def capture_dir_for(card: dict[str, object]) -> Path:
    lua_script = str(card.get("lua_script", ""))
    if "broad_scan" in lua_script:
        return REPO_ROOT / "rom_analysis" / "manual_screen_dump_broad_scan"
    if "v041" in lua_script:
        return REPO_ROOT / "rom_analysis" / "manual_screen_dump_v041"
    if "v04" in lua_script:
        return REPO_ROOT / "rom_analysis" / "manual_screen_dump_v04"
    return REPO_ROOT / "rom_analysis" / "manual_screen_dump"


def read_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def card_status(card: dict[str, object]) -> dict[str, object]:
    capture_dir = capture_dir_for(card)
    record_files = sorted(capture_dir.glob("manual_frame_*_target_records.tsv"))
    wanted_label = str(card.get("label", ""))
    wanted_rom = normalize_rom_hit(card.get("rom_hit", ""))
    checked_records = 0
    matched = []
    saw_any_target = False

    for records_path in record_files:
        rows = read_records(records_path)
        checked_records += len(rows)
        frame = rows[0].get("frame", "?") if rows else "?"
        for row in rows:
            same_label = row.get("label", "") == wanted_label
            same_rom = normalize_rom_hit(row.get("rom_hit", "")) == wanted_rom
            if same_label or same_rom:
                saw_any_target = True
            if (same_label or same_rom) and row.get("active_expected_match", "").lower() == "true":
                matched.append(
                    {
                        "records": rel(records_path),
                        "frame": frame,
                        "label": row.get("label", ""),
                        "rom_hit": normalize_rom_hit(row.get("rom_hit", "")),
                        "cpu_range": row.get("cpu_range", ""),
                        "expected_bytes": row.get("expected_bytes", ""),
                        "record_snapshot": row.get("record_snapshot", ""),
                    }
                )

    if matched:
        status = "match_found_needs_visual_verdict"
        next_step = "Inspect the captured screen/PPU viewer evidence, then promote or reject this card."
    elif record_files and saw_any_target:
        status = "target_seen_no_active_match"
        next_step = "The target was checked on captured screens but did not match; capture the exact intended screen."
    elif record_files:
        status = "dump_exists_wrong_target_set_or_screen"
        next_step = "A dump exists, but this card's target was not present in those records; rerun the listed Lua script on the intended screen."
    else:
        status = "no_dump_records"
        next_step = "Manually reach the screen in FCEUX and run the card's Lua script."

    return {
        "task": card.get("task", ""),
        "priority": card.get("priority", ""),
        "kind": card.get("kind", ""),
        "label": wanted_label,
        "rom_hit": wanted_rom,
        "capture_dir": rel(capture_dir),
        "record_file_count": len(record_files),
        "records_checked": checked_records,
        "status": status,
        "matches": matched,
        "next_step": next_step,
    }


def make_payload() -> dict[str, object]:
    cards_payload = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
    statuses = [card_status(card) for card in cards_payload["cards"]]
    counts: dict[str, int] = {}
    for row in statuses:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    return {
        "source": rel(CARDS_JSON),
        "summary": {
            "card_count": len(statuses),
            "status_counts": counts,
            "rule": "A byte match from a manual dump is evidence, but final promotion still needs visual screen context.",
        },
        "cards": statuses,
    }


def write_markdown(payload: dict[str, object]) -> None:
    lines = [
        "# Manual Capture Status",
        "",
        "This file is generated from `manual_capture_cards.json` plus any `manual_frame_*_target_records.tsv` files.",
        "",
        "## Summary",
        "",
        f"- Cards: **{payload['summary']['card_count']}**",
        "- Rule: a byte match is useful evidence, but final promotion still needs visual screen context.",
        "",
        "| status | count |",
        "| --- | ---: |",
    ]
    for status, count in sorted(payload["summary"]["status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")

    lines += [
        "",
        "## Cards",
        "",
        "| task | priority | status | ROM hit | records | matches | next step |",
        "| ---: | ---: | --- | --- | ---: | ---: | --- |",
    ]
    for card in payload["cards"]:
        lines.append(
            f"| {card['task']} | {card['priority']} | `{card['status']}` | "
            f"`{card['rom_hit']}` | {card['record_file_count']} | {len(card['matches'])} | "
            f"{card['next_step']} |"
        )

    lines += [
        "",
        "## Match Details",
        "",
    ]
    any_match = False
    for card in payload["cards"]:
        for match in card["matches"]:
            any_match = True
            lines += [
                f"### Task {card['task']} `{card['rom_hit']}`",
                "",
                f"- Records: `{match['records']}`",
                f"- Frame: `{match['frame']}`",
                f"- Label: `{match['label']}`",
                f"- CPU range: `{match['cpu_range']}`",
                f"- Expected bytes: `{match['expected_bytes']}`",
                f"- Snapshot: `{match['record_snapshot']}`",
                "",
            ]
    if not any_match:
        lines.append("_No manual capture card has an active byte match yet._")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"cards={payload['summary']['card_count']} statuses={payload['summary']['status_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

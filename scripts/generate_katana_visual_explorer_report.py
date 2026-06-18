#!/usr/bin/env python3
"""Summarize the focused Katana visual explorer run."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


RUN_DIR = REPO_ROOT / "rom_analysis" / "katana_visual_explorer_v042"
SUMMARY_TSV = RUN_DIR / "katana_explorer_summary.tsv"
TARGET_FRAME = "2385"
TARGET_ROM = "ROM+0x07227"
OUT_JSON = RUN_DIR / "report.json"
OUT_MD = RUN_DIR / "report.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def target_records_for_frame(frame: str) -> list[dict[str, str]]:
    path = RUN_DIR / f"manual_frame_{int(frame):06d}_target_records.tsv"
    return read_tsv(path) if path.exists() else []


def make_payload() -> dict[str, object]:
    summary_rows = read_tsv(SUMMARY_TSV)
    item_records = target_records_for_frame(TARGET_FRAME)
    katana_record = next((row for row in item_records if row.get("rom_hit") == TARGET_ROM), {})
    key_frames = [
        {
            "frame": "1905",
            "route": "start_right_a",
            "role": "main menu with item/status choices visible",
            "image": "rom_analysis/katana_visual_explorer_v042/manual_frame_001906_screen.png",
        },
        {
            "frame": TARGET_FRAME,
            "route": "menu_left_a",
            "role": "item list reached; current inventory says empty",
            "image": "rom_analysis/katana_visual_explorer_v042/manual_frame_002385_screen.png",
        },
    ]
    return {
        "source": {
            "lua": "lua/kunio_katana_visual_explorer_v042.lua",
            "summary": str(SUMMARY_TSV.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "summary": {
            "frames_recorded": len([row for row in summary_rows if row.get("route") != "done"]),
            "final_frame": summary_rows[-1].get("frame") if summary_rows else "",
            "item_list_frame": TARGET_FRAME,
            "katana_rom_hit": TARGET_ROM,
            "katana_active_match_on_item_list": katana_record.get("active_expected_match", ""),
            "katana_record_snapshot_on_item_list": katana_record.get("record_snapshot", ""),
            "decision": (
                "The route now reaches the item-list context automatically, but the list is empty. "
                "Do not mark Katana visually confirmed until the item is acquired or injected and the label is visible."
            ),
            "next_step": "Find or set the inventory state that makes the Katana item label appear on the reached item-list screen.",
        },
        "key_frames": key_frames,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Katana Visual Explorer v0.4.2",
        "",
        "Focused route evidence for the primary visual target `0x07227` / `Katana`.",
        "",
        "## Summary",
        "",
        f"- Frames recorded: **{summary['frames_recorded']}**",
        f"- Final frame: **{summary['final_frame']}**",
        f"- Item-list frame: **{summary['item_list_frame']}**",
        f"- Katana ROM hit: `{summary['katana_rom_hit']}`",
        f"- Katana active match on item-list screen: `{summary['katana_active_match_on_item_list']}`",
        f"- Item-list snapshot at Katana CPU range: `{summary['katana_record_snapshot_on_item_list']}`",
        f"- Decision: {summary['decision']}",
        f"- Next step: {summary['next_step']}",
        "",
        "## Key Frames",
        "",
        "| frame | route | role | image |",
        "| ---: | --- | --- | --- |",
    ]
    for row in payload["key_frames"]:
        lines.append(f"| {row['frame']} | `{row['route']}` | {row['role']} | `{row['image']}` |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"katana_active_match_on_item_list={payload['summary']['katana_active_match_on_item_list']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

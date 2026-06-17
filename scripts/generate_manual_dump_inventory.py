#!/usr/bin/env python3
"""Inventory manual FCEUX dump folders and evidence files."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


DUMP_DIRS = [
    ("base", REPO_ROOT / "rom_analysis" / "manual_screen_dump"),
    ("v04", REPO_ROOT / "rom_analysis" / "manual_screen_dump_v04"),
    ("v041", REPO_ROOT / "rom_analysis" / "manual_screen_dump_v041"),
    ("v042", REPO_ROOT / "rom_analysis" / "manual_screen_dump_v042"),
    ("broad_scan", REPO_ROOT / "rom_analysis" / "manual_screen_dump_broad_scan"),
]
OUT_JSON = REPO_ROOT / "rom_analysis" / "manual_dump_inventory.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "manual_dump_inventory.md"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_record_count(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    matches = sum(1 for row in rows if str(row.get("active_expected_match", "")).lower() == "true")
    return len(rows), matches


def latest(paths: list[Path]) -> Path | None:
    return sorted(paths)[-1] if paths else None


def load_summary_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def inventory_dir(label: str, path: Path) -> dict[str, object]:
    record_files = sorted(path.glob("manual_frame_*_target_records.tsv")) if path.exists() else []
    screenshot_files = sorted(path.glob("manual_frame_*_screen.gd")) if path.exists() else []
    meta_files = sorted(path.glob("manual_frame_*_meta.txt")) if path.exists() else []
    latest_records = latest(record_files)
    latest_screenshot = latest(screenshot_files)
    latest_meta = latest(meta_files)
    latest_record_rows, latest_record_matches = read_record_count(latest_records) if latest_records else (0, 0)
    summary_json = path / "summary.json"
    summary_md = path / "summary.md"
    summary_payload = load_summary_json(summary_json)
    summary_active_matches = int(summary_payload.get("active_expected_matches", 0) or 0)
    summary_targets_checked = int(summary_payload.get("targets_checked", 0) or 0)
    summary_frame = str(summary_payload.get("frame", "") or "")
    summary_screenshot = str(summary_payload.get("latest_screenshot", "") or "")
    status = "no_dump_records"
    if (record_files and latest_record_matches) or summary_active_matches:
        status = "has_active_match_records"
    elif record_files:
        status = "has_dump_records_no_active_match"
    return {
        "label": label,
        "path": rel(path),
        "exists": path.exists(),
        "record_file_count": len(record_files),
        "screenshot_file_count": len(screenshot_files),
        "meta_file_count": len(meta_files),
        "latest_records": rel(latest_records) if latest_records else "",
        "latest_screenshot": rel(latest_screenshot) if latest_screenshot else "",
        "latest_meta": rel(latest_meta) if latest_meta else "",
        "latest_record_rows": latest_record_rows,
        "latest_record_active_matches": latest_record_matches,
        "summary_frame": summary_frame,
        "summary_targets_checked": summary_targets_checked,
        "summary_active_matches": summary_active_matches,
        "summary_latest_screenshot": summary_screenshot,
        "summary_json": rel(summary_json) if summary_json.exists() else "",
        "summary_md": rel(summary_md) if summary_md.exists() else "",
        "status": status,
    }


def make_payload() -> dict[str, object]:
    dirs = [inventory_dir(label, path) for label, path in DUMP_DIRS]
    counts: dict[str, int] = {}
    for row in dirs:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    return {
        "summary": {
            "dump_dirs": len(dirs),
            "total_record_files": sum(int(row["record_file_count"]) for row in dirs),
            "total_screenshot_files": sum(int(row["screenshot_file_count"]) for row in dirs),
            "total_latest_active_matches": sum(int(row["latest_record_active_matches"]) for row in dirs),
            "total_summary_active_matches": sum(int(row["summary_active_matches"]) for row in dirs),
            "status_counts": counts,
            "rule": "A screenshot file is visual evidence to review, but patch promotion still requires explicit visual_review confirmation.",
        },
        "dump_dirs": dirs,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Manual Dump Inventory",
        "",
        "This inventory shows whether the manual FCEUX dump folders contain record files, screenshots, and summaries.",
        "",
        "## Summary",
        "",
        f"- Dump dirs: **{summary['dump_dirs']}**",
        f"- Total target-record files: **{summary['total_record_files']}**",
        f"- Total screenshot files: **{summary['total_screenshot_files']}**",
        f"- Active matches in latest records: **{summary['total_latest_active_matches']}**",
        f"- Active matches in summaries: **{summary['total_summary_active_matches']}**",
        "",
        "| folder | status | record files | screenshots | latest active matches | summary frame | summary matches | latest records | latest screenshot | summary |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in payload["dump_dirs"]:
        summary_path = row["summary_md"] or row["summary_json"] or "-"
        screenshot = row["latest_screenshot"] or row["summary_latest_screenshot"] or "-"
        lines.append(
            f"| `{row['label']}` | `{row['status']}` | {row['record_file_count']} | "
            f"{row['screenshot_file_count']} | {row['latest_record_active_matches']} | "
            f"{row['summary_frame'] or '-'} | {row['summary_active_matches']} | "
            f"`{row['latest_records'] or '-'}` | `{screenshot}` | `{summary_path}` |"
        )
    lines += [
        "",
        "## Rule",
        "",
        "- `.gd` screenshots are kept as visual evidence from FCEUX `gui.gdscreenshot()`.",
        "- A target-record byte match is not enough for promotion; confirm the visible screen context with `record_visual_review.py`.",
        "- If all folders show `no_dump_records`, do not extend autoplay. Use `reference_capture_plan.md` to pick a concrete screen.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "record_files={total_record_files} screenshots={total_screenshot_files} active_latest={total_latest_active_matches}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

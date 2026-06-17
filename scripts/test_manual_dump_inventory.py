#!/usr/bin/env python3
"""Check the manual dump inventory for the current checked-in state."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


INVENTORY_JSON = REPO_ROOT / "rom_analysis" / "manual_dump_inventory.json"
INVENTORY_MD = REPO_ROOT / "rom_analysis" / "manual_dump_inventory.md"


def main() -> int:
    payload = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
    errors = []
    if payload["summary"]["dump_dirs"] != 5:
        errors.append(f"expected 5 dump dirs, got {payload['summary']['dump_dirs']}")
    if payload["summary"]["total_record_files"] != 0:
        errors.append("checked-in manual dump inventory should not contain record files")
    if payload["summary"]["total_screenshot_files"] != 0:
        errors.append("checked-in manual dump inventory should not contain screenshot files")
    if payload["summary"]["total_summary_active_matches"] != 0:
        errors.append("checked-in manual dump inventory should not contain summary active matches")
    if set(payload["summary"]["status_counts"]) != {"no_dump_records"}:
        errors.append(f"unexpected status counts: {payload['summary']['status_counts']}")
    for row in payload["dump_dirs"]:
        for key in ["summary_frame", "summary_targets_checked", "summary_active_matches", "summary_latest_screenshot"]:
            if key not in row:
                errors.append(f"{key!r} missing from {row.get('label')}")

    markdown = INVENTORY_MD.read_text(encoding="utf-8")
    for expected in ["Manual Dump Inventory", "Active matches in summaries", "reference_capture_plan.md", "record_visual_review.py"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: manual dump inventory matches current no-dump checked-in state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check the release test checklist is self-contained enough to use."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


CHECKLIST_JSON = REPO_ROOT / "rom_analysis" / "release_test_checklist.json"
CHECKLIST_MD = REPO_ROOT / "rom_analysis" / "release_test_checklist.md"


def main() -> int:
    payload = json.loads(CHECKLIST_JSON.read_text(encoding="utf-8"))
    rows = payload["priority_manual_checks"]
    errors = []
    if payload["summary"]["priority_manual_checks"] != 7:
        errors.append(f"expected 7 priority manual checks, got {payload['summary']['priority_manual_checks']}")
    if not rows or rows[0].get("source_display") != "へいしち":
        errors.append("expected Heishichi to be the first manual proof target")
    markdown = CHECKLIST_MD.read_text(encoding="utf-8")
    for expected in [
        "Release Test Checklist",
        "python scripts/apply_primary_patch.py",
        "lua/kunio_manual_broad_scan_dump.lua",
        "python scripts/record_visual_review.py",
        "0x0440C",
    ]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from checklist")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: release test checklist includes apply, capture, and review steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check the reference-guided capture plan is useful and non-promotional."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


PLAN_JSON = REPO_ROOT / "rom_analysis" / "reference_capture_plan.json"
PLAN_MD = REPO_ROOT / "rom_analysis" / "reference_capture_plan.md"


def main() -> int:
    payload = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    rows = payload["focused_capture_plan"]
    offsets = {str(row["rom_offset"]).upper() for row in rows}
    errors = []
    if payload["summary"]["focused_rows"] != 20:
        errors.append(f"expected 20 focused rows, got {payload['summary']['focused_rows']}")
    if not any(row["promotable_after_screen_proof"] for row in rows):
        errors.append("focused plan has no length-safe promotion candidates")
    for expected in {"0X0440C", "0X052A5", "0X06294"}:
        if expected not in offsets:
            errors.append(f"{expected} missing from focused capture plan")
    markdown = PLAN_MD.read_text(encoding="utf-8")
    for expected in ["Reference-Guided Capture Plan", "does not treat YouTube", "대장간", "타츠지"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: reference capture plan contains focused non-promotional targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

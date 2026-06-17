#!/usr/bin/env python3
"""Check that the broad translation capture queue has readable labels."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


QUEUE_JSON = REPO_ROOT / "rom_analysis" / "translation_scan_capture_queue.json"
QUEUE_MD = REPO_ROOT / "rom_analysis" / "translation_scan_capture_queue.md"


def main() -> int:
    payload = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    rows = payload["queue"]
    errors = []
    if not rows:
        errors.append("queue is empty")
    for key in ["source_display", "korean_display", "meaning", "screen_hint"]:
        missing = [row["rom_offset"] for row in rows if not row.get(key)]
        if missing:
            errors.append(f"{key} missing for {missing[:5]}")

    known_tatsuji = [row for row in rows if row.get("romaji") == "Tatsuji"]
    if not known_tatsuji:
        errors.append("Tatsuji rows are missing from the queue")
    elif not any(row.get("source_display") == "たつじ" and row.get("korean_display") == "타츠지" for row in known_tatsuji):
        errors.append("Tatsuji rows are not using readable display labels")

    markdown = QUEUE_MD.read_text(encoding="utf-8")
    for expected in ["human hint", "boss/name label"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown queue")
    for expected in ["expected text", "screen hint", "타츠지"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown queue")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: translation capture queue includes readable display labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

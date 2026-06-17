#!/usr/bin/env python3
"""Check the v0.4.2 manual proof packet stays useful at FCEUX time."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


PACKET_JSON = REPO_ROOT / "rom_analysis" / "v042_manual_proof_packet.json"
PACKET_MD = REPO_ROOT / "rom_analysis" / "v042_manual_proof_packet.md"


def main() -> int:
    payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
    tasks = payload["tasks"]
    errors: list[str] = []
    if len(tasks) != 7:
        errors.append(f"expected 7 proof tasks, got {len(tasks)}")
    for key in ["romaji", "meaning", "screen_hint", "capture_lua"]:
        missing = [task["rom_offset"] for task in tasks if not task.get(key)]
        if missing:
            errors.append(f"{key} missing for {missing[:5]}")

    markdown = PACKET_MD.read_text(encoding="utf-8")
    for expected in ["human hint", "blacksmith/stage label", "boss/name label", "name/dialogue label"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown packet")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: v0.4.2 manual proof packet includes human hints for all tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

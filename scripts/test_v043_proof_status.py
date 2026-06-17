#!/usr/bin/env python3
"""Check the generated v0.4.3 proof status report invariants."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


STATUS_JSON = REPO_ROOT / "rom_analysis" / "v043_proof_status.json"
STATUS_MD = REPO_ROOT / "rom_analysis" / "v043_proof_status.md"


def main() -> int:
    payload = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
    rows = payload["rows"]
    errors = []
    if payload["summary"]["rows"] != 7:
        errors.append(f"expected 7 proof rows, got {payload['summary']['rows']}")
    for key in ["cpu_read_match_present", "visual_context_confirmed", "applied_in_v043_build"]:
        if any(row[key] for row in rows):
            errors.append(f"current checked-in proof status should have no {key}=true rows")
    if set(payload["summary"]["status_counts"]) != {"needs_manual_capture"}:
        errors.append(f"unexpected status counts: {payload['summary']['status_counts']}")
    for key in ["meaning", "screen_hint"]:
        missing = [row["rom_offset"] for row in rows if not row.get(key)]
        if missing:
            errors.append(f"{key} missing for {missing[:5]}")

    markdown = STATUS_MD.read_text(encoding="utf-8")
    for expected in ["human hint", "blacksmith/stage label", "boss/name label", "name/dialogue label"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown")
    for expected in ["v0.4.3 Proof Status", "needs_manual_capture", "かじや", "たつじ", "へいしち"]:
        if expected not in markdown:
            errors.append(f"{expected!r} missing from markdown")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: v0.4.3 proof status matches current checked-in gate state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

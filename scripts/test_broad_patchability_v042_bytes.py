#!/usr/bin/env python3
"""Check broad-scan patchability planned bytes against v0.4.2 readiness."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


PATCHABILITY_JSON = REPO_ROOT / "rom_analysis" / "broad_scan_patchability.json"
READINESS_JSON = REPO_ROOT / "rom_analysis" / "v042_text_promotion_readiness.json"


def main() -> int:
    patchability = json.loads(PATCHABILITY_JSON.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS_JSON.read_text(encoding="utf-8"))
    ready_by_offset = {
        str(row["rom_offset"]).upper(): row
        for row in readiness["candidates"]
    }
    errors = []
    summary = patchability["summary"]
    if summary.get("promotion_candidates_font_ready_after_v042") != summary.get("promotion_candidates_after_screen_proof"):
        errors.append("not every broad promotion candidate is font-ready after v0.4.2")
    if summary.get("additional_glyphs_after_v042_if_promoted") != 0:
        errors.append("v0.4.2 still reports missing glyphs for broad promotion candidates")

    for row in patchability["promotion_candidates"]:
        offset = str(row["rom_offset"]).upper()
        readiness_row = ready_by_offset.get(offset)
        if readiness_row is None:
            errors.append(f"{offset} missing from v0.4.2 readiness")
            continue
        patchability_bytes = list(row.get("planned_prg_bytes_after_v042", []))
        readiness_bytes = list(readiness_row.get("planned_prg_bytes", []))
        if patchability_bytes != readiness_bytes:
            errors.append(f"{offset} planned bytes mismatch: {patchability_bytes} != {readiness_bytes}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: broad patchability v0.4.2 planned bytes match readiness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

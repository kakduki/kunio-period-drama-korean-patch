#!/usr/bin/env python3
"""Rank object/enemy-state RAM candidates for boss/scene cheat probing."""

from __future__ import annotations

import json

from generate_state_cheat_probe_candidates import address_rows, load_snapshots
from rom_utils import REPO_ROOT


OUT_JSON = REPO_ROOT / "rom_analysis" / "object_state_probe_candidates.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "object_state_probe_candidates.md"
OBJECT_START = 0x0300
OBJECT_END = 0x04FF


def int_address(row: dict[str, object]) -> int:
    return int(str(row["address"]), 16)


def slot_hint(addr: int) -> str:
    offset = addr - OBJECT_START
    column = offset % 0x10
    block = offset // 0x10
    return f"block={block:02X} column={column:01X}"


def make_payload() -> dict[str, object]:
    snapshots = load_snapshots()
    rows = [
        row
        for row in address_rows(snapshots)
        if OBJECT_START <= int_address(row) <= OBJECT_END
    ]
    for row in rows:
        row["slot_hint"] = slot_hint(int_address(row))
    return {
        "summary": {
            "snapshots": len(snapshots),
            "object_range": f"0x{OBJECT_START:04X}-0x{OBJECT_END:04X}",
            "candidate_addresses": len(rows),
            "top_candidate_count": min(32, len(rows)),
            "recommended_use": "Probe these before more runtime-flag writes; they are more likely to represent actors, enemies, route objects, or spawn state.",
        },
        "top_candidates": rows[:32],
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Object State Probe Candidates",
        "",
        "This report filters the state-cheat scan to CPU RAM `$0300-$04FF`, the likely object/enemy/route-state area.",
        "Use it for boss-spawn or enemy-clear cheat discovery before trying more isolated runtime-flag writes.",
        "",
        "## Summary",
        "",
        f"- Snapshots compared: **{summary['snapshots']}**",
        f"- Object range: `{summary['object_range']}`",
        f"- Candidate addresses: **{summary['candidate_addresses']}**",
        f"- Top candidates shown: **{summary['top_candidate_count']}**",
        f"- Recommended use: {summary['recommended_use']}",
        "",
        "## Top Object/Enemy Candidates",
        "",
        "| address | slot hint | score | unique | changes | late values | values by group |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["top_candidates"]:
        late_values = ", ".join(f"{group}={value}" for group, value in row["late_values"].items())
        by_group = ", ".join(f"{group}={values}" for group, values in row["values_by_group"].items())
        lines.append(
            f"| `{row['address']}` | `{row['slot_hint']}` | {row['score']} | {row['unique_values']} | "
            f"{row['adjacent_changes']} | {late_values} | {by_group} |"
        )
    lines += [
        "",
        "## Next Probe",
        "",
        "Test one address and one value at a time with `lua/kunio_state_single_byte_probe.lua`.",
        "Prefer late `input_dialogue` values when trying to reproduce dialogue-like screens, but keep selected PNG evidence only when a visible state changes.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"top_candidate_count={payload['summary']['top_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

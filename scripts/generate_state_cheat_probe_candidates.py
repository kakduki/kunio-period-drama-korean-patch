#!/usr/bin/env python3
"""Rank RAM addresses that may help build scene/route cheat probes."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from rom_utils import REPO_ROOT


OUT_JSON = REPO_ROOT / "rom_analysis" / "state_cheat_probe_candidates.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "state_cheat_probe_candidates.md"

CAPTURE_DIRS = [
    ("input_dialogue", REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042"),
    ("katana_menu_route", REPO_ROOT / "rom_analysis" / "katana_visual_explorer_v042"),
]

ADDRESS_ROLES = {
    range(0x0000, 0x0100): "zero_page_engine_state",
    range(0x0100, 0x0200): "stack_or_transient",
    range(0x0200, 0x0300): "sprite_oam_shadow",
    range(0x0300, 0x0500): "object_or_route_state",
    range(0x0500, 0x0600): "menu_inventory_or_ui_state",
    range(0x0600, 0x0700): "nametable_or_text_buffer",
    range(0x0700, 0x0800): "runtime_flags",
}

LOW_VALUE_RANGES = [
    range(0x0100, 0x0200),
    range(0x0200, 0x0300),
    range(0x0600, 0x0700),
]


@dataclass(frozen=True)
class Snapshot:
    group: str
    frame: int
    path: Path
    data: bytes


def frame_from_name(path: Path) -> int:
    match = re.search(r"(?:manual_)?frame_(\d+)", path.name)
    if not match:
        return -1
    return int(match.group(1))


def role_for(addr: int) -> str:
    for addr_range, role in ADDRESS_ROLES.items():
        if addr in addr_range:
            return role
    return "unknown"


def low_value(addr: int) -> bool:
    return any(addr in addr_range for addr_range in LOW_VALUE_RANGES)


def load_snapshots() -> list[Snapshot]:
    snapshots: list[Snapshot] = []
    for group, folder in CAPTURE_DIRS:
        for path in sorted(folder.glob("*cpu_ram.bin"), key=frame_from_name):
            data = path.read_bytes()
            if len(data) < 0x800:
                continue
            snapshots.append(Snapshot(group=group, frame=frame_from_name(path), path=path, data=data[:0x800]))
    return snapshots


def address_rows(snapshots: list[Snapshot]) -> list[dict[str, object]]:
    if not snapshots:
        return []
    rows: list[dict[str, object]] = []
    groups = sorted({snapshot.group for snapshot in snapshots})
    for addr in range(0x800):
        values = [snapshot.data[addr] for snapshot in snapshots]
        unique_values = sorted(set(values))
        if len(unique_values) < 2:
            continue
        group_values: dict[str, set[int]] = {
            group: {snapshot.data[addr] for snapshot in snapshots if snapshot.group == group}
            for group in groups
        }
        group_separation = 0
        if len(groups) >= 2:
            first, second = groups[0], groups[1]
            if group_values[first].isdisjoint(group_values[second]):
                group_separation = 1
        adjacent_changes = sum(
            1
            for before, after in zip(snapshots, snapshots[1:])
            if before.group == after.group and before.data[addr] != after.data[addr]
        )
        late_values = {
            group: next(
                (snapshot.data[addr] for snapshot in reversed(snapshots) if snapshot.group == group),
                None,
            )
            for group in groups
        }
        score = len(unique_values) + adjacent_changes + (6 * group_separation)
        if low_value(addr):
            score -= 4
        if role_for(addr) in {"zero_page_engine_state", "object_or_route_state", "runtime_flags"}:
            score += 2
        rows.append(
            {
                "address": f"0x{addr:04X}",
                "role": role_for(addr),
                "score": score,
                "unique_values": len(unique_values),
                "adjacent_changes": adjacent_changes,
                "group_separation": bool(group_separation),
                "values_by_group": {
                    group: " ".join(f"{value:02X}" for value in sorted(group_values[group]))
                    for group in groups
                },
                "late_values": {
                    group: (f"0x{value:02X}" if value is not None else "-")
                    for group, value in late_values.items()
                },
            }
        )
    return sorted(rows, key=lambda row: (-int(row["score"]), str(row["address"])))


def make_payload() -> dict[str, object]:
    snapshots = load_snapshots()
    rows = address_rows(snapshots)
    return {
        "sources": [
            {
                "group": group,
                "folder": str(folder.relative_to(REPO_ROOT)).replace("\\", "/"),
                "cpu_ram_snapshots": len(list(folder.glob("*cpu_ram.bin"))),
            }
            for group, folder in CAPTURE_DIRS
        ],
        "summary": {
            "snapshots": len(snapshots),
            "candidate_addresses": len(rows),
            "top_candidate_count": min(32, len(rows)),
            "recommended_use": "Use these addresses as the first watch/write candidates for route cheats, not as confirmed cheat codes.",
        },
        "top_candidates": rows[:32],
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# State Cheat Probe Candidates",
        "",
        "This report ranks CPU RAM addresses that change across existing route/dialogue/menu captures.",
        "It is meant to narrow the next FCEUX Lua cheat search for scene warps, enemy-clear flags, and boss-spawn state.",
        "",
        "## Summary",
        "",
        f"- Snapshots compared: **{summary['snapshots']}**",
        f"- Candidate addresses: **{summary['candidate_addresses']}**",
        f"- Top candidates shown: **{summary['top_candidate_count']}**",
        f"- Recommended use: {summary['recommended_use']}",
        "",
        "## Sources",
        "",
        "| group | folder | CPU RAM snapshots |",
        "| --- | --- | ---: |",
    ]
    for source in payload["sources"]:
        lines.append(f"| `{source['group']}` | `{source['folder']}` | {source['cpu_ram_snapshots']} |")
    lines += [
        "",
        "## Top RAM Candidates",
        "",
        "| address | role | score | unique | changes | separates groups | late values | values by group |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in payload["top_candidates"]:
        late_values = ", ".join(f"{group}={value}" for group, value in row["late_values"].items())
        by_group = ", ".join(f"{group}={values}" for group, values in row["values_by_group"].items())
        lines.append(
            f"| `{row['address']}` | `{row['role']}` | {row['score']} | {row['unique_values']} | "
            f"{row['adjacent_changes']} | {str(row['group_separation']).lower()} | {late_values} | {by_group} |"
        )
    lines += [
        "",
        "## Next Probe",
        "",
        "Build a Lua script that watches the top zero-page/object/runtime candidates while entering, leaving, or forcing route screens.",
        "Avoid broad writes. Write one suspected state byte at a time and capture both CPU records and a screenshot.",
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

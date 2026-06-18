#!/usr/bin/env python3
"""Plan paired object-state probes from existing RAM snapshots."""

from __future__ import annotations

import json
from collections import defaultdict

from generate_state_cheat_probe_candidates import load_snapshots
from rom_utils import REPO_ROOT


OUT_JSON = REPO_ROOT / "rom_analysis" / "object_state_pair_plan.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "object_state_pair_plan.md"
OBJECT_START = 0x0300
OBJECT_END = 0x04FF
BLOCK_SIZE = 0x10


def group_values(snapshots: list[object], addr: int) -> dict[str, set[int]]:
    groups = sorted({snapshot.group for snapshot in snapshots})
    return {
        group: {snapshot.data[addr] for snapshot in snapshots if snapshot.group == group}
        for group in groups
    }


def late_values(snapshots: list[object], addr: int) -> dict[str, int | None]:
    groups = sorted({snapshot.group for snapshot in snapshots})
    return {
        group: next((snapshot.data[addr] for snapshot in reversed(snapshots) if snapshot.group == group), None)
        for group in groups
    }


def changing_addresses(snapshots: list[object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for addr in range(OBJECT_START, OBJECT_END + 1):
        values = {snapshot.data[addr] for snapshot in snapshots}
        if len(values) < 2:
            continue
        by_group = group_values(snapshots, addr)
        late = late_values(snapshots, addr)
        changes = sum(
            1
            for before, after in zip(snapshots, snapshots[1:])
            if before.group == after.group and before.data[addr] != after.data[addr]
        )
        rows.append(
            {
                "address": f"0x{addr:04X}",
                "block": f"0x{addr - ((addr - OBJECT_START) % BLOCK_SIZE):04X}",
                "column": f"0x{(addr - OBJECT_START) % BLOCK_SIZE:X}",
                "unique_values": len(values),
                "changes": changes,
                "late_values": {
                    group: (f"0x{value:02X}" if value is not None else "-")
                    for group, value in late.items()
                },
                "values_by_group": {
                    group: " ".join(f"{value:02X}" for value in sorted(values))
                    for group, values in by_group.items()
                },
            }
        )
    return rows


def make_payload() -> dict[str, object]:
    snapshots = load_snapshots()
    rows = changing_addresses(snapshots)
    blocks: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        blocks[str(row["block"])].append(row)
    block_rows: list[dict[str, object]] = []
    for block, items in blocks.items():
        ranked = sorted(items, key=lambda row: (-int(row["changes"]), -int(row["unique_values"]), str(row["address"])))
        score = sum(int(row["changes"]) + int(row["unique_values"]) for row in ranked)
        block_rows.append(
            {
                "block": block,
                "score": score,
                "changing_fields": len(ranked),
                "recommended_fields": ranked[:4],
                "recommended_probe": [
                    {
                        "address": row["address"],
                        "value": row["late_values"].get("input_dialogue", "-"),
                    }
                    for row in ranked[:4]
                ],
            }
        )
    block_rows.sort(key=lambda row: (-int(row["score"]), str(row["block"])))
    return {
        "summary": {
            "snapshots": len(snapshots),
            "object_range": f"0x{OBJECT_START:04X}-0x{OBJECT_END:04X}",
            "candidate_blocks": len(block_rows),
            "top_block_count": min(12, len(block_rows)),
            "recommended_use": "Use the recommended fields as a small paired-write queue; do not treat any block as confirmed until screenshots and target records change.",
        },
        "top_blocks": block_rows[:12],
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Object State Pair Plan",
        "",
        "This groups changing `$0300-$04FF` addresses into 16-byte object/state blocks.",
        "The goal is to avoid wasting runs on adjacent single-byte writes when the game likely stores actor state across several fields.",
        "",
        "## Summary",
        "",
        f"- Snapshots compared: **{summary['snapshots']}**",
        f"- Object range: `{summary['object_range']}`",
        f"- Candidate blocks: **{summary['candidate_blocks']}**",
        f"- Top blocks shown: **{summary['top_block_count']}**",
        f"- Recommended use: {summary['recommended_use']}",
        "",
    ]
    for block in payload["top_blocks"]:
        lines += [
            f"## Block {block['block']}",
            "",
            f"- Score: **{block['score']}**",
            f"- Changing fields: **{block['changing_fields']}**",
            "- Recommended paired probe:",
        ]
        for probe in block["recommended_probe"]:
            lines.append(f"  - `{probe['address']} = {probe['value']}`")
        lines += [
            "",
            "| address | column | unique | changes | late values | values by group |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ]
        for row in block["recommended_fields"]:
            late_values = ", ".join(f"{group}={value}" for group, value in row["late_values"].items())
            by_group = ", ".join(f"{group}={values}" for group, values in row["values_by_group"].items())
            lines.append(
                f"| `{row['address']}` | `{row['column']}` | {row['unique_values']} | {row['changes']} | "
                f"{late_values} | {by_group} |"
            )
        lines.append("")
    lines += [
        "## Next Probe",
        "",
        "Add a paired-write Lua mode or run a tiny custom Lua probe for the top block only.",
        "Start with block `0x04F0` because `$04FA` and `$04FB` were individually tested, then write the recommended block values together if single-byte tests remain unhelpful.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"top_block_count={payload['summary']['top_block_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

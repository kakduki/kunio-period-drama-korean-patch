#!/usr/bin/env python3
"""Generate a prioritized manual FCEUX capture queue.

The queue is for screens that should be reached manually, then captured with
lua/kunio_manual_screen_dump.lua. This avoids long blind autoplay runs.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "rom_analysis" / "bank1_offset_status.json"
OUT_MD = ROOT / "rom_analysis" / "manual_capture_queue.md"
OUT_JSON = ROOT / "rom_analysis" / "manual_capture_queue.json"


def priority_for(row: dict[str, object]) -> tuple[int, str]:
    risk = str(row.get("patch_risk", ""))
    evidence = str(row.get("evidence_level", ""))
    category_group = str(row.get("category_group", ""))
    active = int(row.get("runtime_active_expected_matches") or 0)

    if risk == "safe-equal-length" and evidence != "runtime-confirmed":
        if category_group == "items/equipment":
            return (10, "safe equal-length item/equipment candidate; needs screen proof")
        if category_group == "UI/status":
            return (15, "safe equal-length UI/status candidate; needs screen proof")
        if category_group == "event/dialogue-related":
            return (20, "safe equal-length event/dialogue candidate; needs screen proof")
        return (25, "safe equal-length candidate; needs screen proof")

    if risk == "needs-padding-rule" and evidence == "runtime-confirmed":
        return (30, "runtime-confirmed shortened replacement; needs visual padding rule")

    if active == 0 and int(row.get("runtime_hits") or 0) > 0:
        return (45, "runtime address hit but wrong active bank/context; capture exact screen")

    return (80, "defer until higher-value captures are exhausted")


def load_rows() -> list[dict[str, object]]:
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for group_name, group in data.get("groups", {}).items():
        for row in group.get("targets", []):
            item = dict(row)
            item.setdefault("category_group", group_name)
            priority, reason = priority_for(item)
            item["capture_priority"] = priority
            item["capture_reason"] = reason
            rows.append(item)
    return sorted(
        rows,
        key=lambda row: (
            int(row["capture_priority"]),
            str(row.get("category_group", "")),
            str(row.get("rom_hit", "")),
            str(row.get("label", "")),
        ),
    )


def compact_row(row: dict[str, object]) -> dict[str, object]:
    keys = [
        "capture_priority",
        "capture_reason",
        "label",
        "category_group",
        "category",
        "source",
        "source_romaji",
        "source_context",
        "korean",
        "rom_hit",
        "record_cpu_range",
        "expected_bytes",
        "evidence_level",
        "patch_risk",
        "runtime_hits",
        "runtime_active_expected_matches",
        "in_watch_range",
    ]
    return {key: row.get(key) for key in keys if key in row}


def main() -> int:
    rows = load_rows()
    focused = [
        row for row in rows
        if int(row["capture_priority"]) <= 45
    ]
    payload = {
        "source": str(STATUS.relative_to(ROOT)),
        "workflow": "rom_analysis/manual_capture_workflow.md",
        "capture_lua": "lua/kunio_manual_screen_dump.lua",
        "summary_script": "scripts/analyze_manual_screen_dump.py",
        "summary": {
            "total_targets": len(rows),
            "queued_targets": len(focused),
            "safe_equal_length_needing_screen": sum(
                1 for row in focused
                if row.get("patch_risk") == "safe-equal-length"
                and row.get("evidence_level") != "runtime-confirmed"
            ),
            "runtime_padding_blockers": sum(
                1 for row in focused
                if row.get("patch_risk") == "needs-padding-rule"
                and row.get("evidence_level") == "runtime-confirmed"
            ),
            "runtime_wrong_context_targets": sum(
                1 for row in focused
                if int(row.get("runtime_hits") or 0) > 0
                and int(row.get("runtime_active_expected_matches") or 0) == 0
            ),
        },
        "queue": [compact_row(row) for row in focused],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Manual FCEUX Capture Queue",
        "",
        "Use this queue after manually reaching a real dialogue/menu/status screen in FCEUX.",
        "Do not extend blind autoplay runs when the emulator is still on the opening/title screen.",
        "",
        "Workflow:",
        "",
        "1. Manually reach the listed kind of screen in FCEUX.",
        "2. Run `lua/kunio_manual_screen_dump.lua` from FCEUX's Lua window.",
        "3. Run `python scripts/analyze_manual_screen_dump.py`.",
        "4. Promote a patch candidate only when the screen-specific evidence supports it.",
        "",
        "## Summary",
        "",
        f"- Total targets in status report: **{payload['summary']['total_targets']}**",
        f"- Queued high-value targets: **{payload['summary']['queued_targets']}**",
        f"- Safe equal-length targets needing screen proof: **{payload['summary']['safe_equal_length_needing_screen']}**",
        f"- Runtime-confirmed padding blockers: **{payload['summary']['runtime_padding_blockers']}**",
        f"- Runtime-hit/wrong-context targets: **{payload['summary']['runtime_wrong_context_targets']}**",
        "",
        "## Queue",
        "",
        "| priority | reason | group | source | romaji/context | Korean | ROM hit | CPU range | expected | evidence | risk |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in focused:
        cpu_range = row.get("record_cpu_range", [])
        if isinstance(cpu_range, list):
            cpu_text = "-".join(str(part) for part in cpu_range)
        else:
            cpu_text = str(cpu_range or "")
        romaji = str(row.get("source_romaji") or "")
        context = str(row.get("source_context") or "")
        romaji_context = "<br>".join(part for part in [romaji, context] if part) or "-"
        lines.append(
            f"| {row['capture_priority']} | {row['capture_reason']} | "
            f"{row.get('category_group', '')} | `{row.get('source', '')}` | "
            f"{romaji_context} | `{row.get('korean', '')}` | "
            f"`{row.get('rom_hit', '')}` | `{cpu_text}` | "
            f"`{row.get('expected_bytes', '')}` | {row.get('evidence_level', '')} | "
            f"{row.get('patch_risk', '')} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- Priority 10-20 rows are the best next candidates because they are equal-length and should not need padding rules.",
        "- Priority 30 rows are important but blocked until the exact visual padding/terminator behavior is proven.",
        "- Priority 45 rows already produced runtime reads in earlier automation, but the active bytes did not match; these need the exact screen/context.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"queued={len(focused)} total={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

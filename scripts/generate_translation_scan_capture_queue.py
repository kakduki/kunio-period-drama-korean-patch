#!/usr/bin/env python3
"""Create a manual capture queue from the broad translation pattern scan."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_JSON = ROOT / "rom_analysis" / "translation_pattern_scan.json"
OUT_JSON = ROOT / "rom_analysis" / "translation_scan_capture_queue.json"
OUT_MD = ROOT / "rom_analysis" / "translation_scan_capture_queue.md"

CONTROL_LIKE = {0x00, 0xFF, 0xF0, 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE}


def parse_hex_bytes(raw: str) -> list[int]:
    return [int(part, 16) for part in raw.split() if part]


def cpu_address(row: dict[str, object]) -> str:
    prg = int(str(row["prg_offset"]), 16)
    return f"${0x8000 + (prg % 0x4000):04X}"


def priority_for(row: dict[str, object]) -> tuple[int, str, str]:
    data = parse_hex_bytes(str(row["bytes"]))
    has_control = any(byte in CONTROL_LIKE for byte in data)
    bank = int(row["bank16"])
    add = str(row["add"])
    group = str(row["group"])

    if bank == 1 and not has_control and add in {"0x7C", "0x80", "0x84"}:
        return (10, "strong Bank 1 text-like hit; capture the related screen", "high")
    if bank == 1 and not has_control:
        return (15, "Bank 1 text-like hit with uncommon shift; capture before patching", "medium")
    if group in {"ui/status", "event/dialogue"} and not has_control:
        return (25, "non-Bank 1 text-like hit; useful for later bank expansion", "medium")
    if bank == 1:
        return (35, "Bank 1 hit but bytes look control-like; verify carefully", "low")
    return (60, "broad scan hit; defer unless the exact screen is reached", "low")


def compact(row: dict[str, object]) -> dict[str, object]:
    priority, reason, confidence = priority_for(row)
    return {
        "priority": priority,
        "confidence": confidence,
        "reason": reason,
        "source": row["source"],
        "romaji": row.get("romaji", ""),
        "korean": row.get("korean", ""),
        "category": row.get("category", ""),
        "group": row.get("group", ""),
        "rom_offset": row["rom_offset"],
        "prg_offset": row["prg_offset"],
        "bank16": row["bank16"],
        "cpu_address_guess": cpu_address(row),
        "add": row["add"],
        "bytes": row["bytes"],
        "score": row["score"],
        "context": row["context"],
    }


def main() -> int:
    scan = json.loads(SCAN_JSON.read_text(encoding="utf-8"))
    rows = [compact(row) for row in scan["top_new_hits"]]
    rows.sort(key=lambda row: (row["priority"], -int(row["score"]), str(row["rom_offset"])))
    focused = rows[:60]

    payload = {
        "source": str(SCAN_JSON.relative_to(ROOT)),
        "workflow": "rom_analysis/manual_capture_workflow.md",
        "capture_lua": "lua/kunio_manual_screen_dump.lua",
        "summary": {
            "scan_new_hits": scan["summary"]["new_hits_total"],
            "queued_hits": len(focused),
            "high_confidence": sum(1 for row in focused if row["confidence"] == "high"),
            "medium_confidence": sum(1 for row in focused if row["confidence"] == "medium"),
            "low_confidence": sum(1 for row in focused if row["confidence"] == "low"),
        },
        "queue": focused,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Translation Scan Capture Queue",
        "",
        "Manual verification queue generated from `translation_pattern_scan`.",
        "These are not approved patch offsets until a real screen dump confirms them.",
        "",
        "## Summary",
        "",
        f"- Scan new hits: **{payload['summary']['scan_new_hits']}**",
        f"- Queued hits: **{payload['summary']['queued_hits']}**",
        f"- High confidence: **{payload['summary']['high_confidence']}**",
        f"- Medium confidence: **{payload['summary']['medium_confidence']}**",
        f"- Low confidence: **{payload['summary']['low_confidence']}**",
        "",
        "## Queue",
        "",
        "| priority | confidence | source | korean | group | ROM | bank | CPU guess | add | bytes | reason |",
        "| ---: | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for row in focused:
        lines.append(
            f"| {row['priority']} | {row['confidence']} | {row['source']} | {row['korean']} | "
            f"{row['group']} | `{row['rom_offset']}` | {row['bank16']} | `{row['cpu_address_guess']}` | "
            f"`{row['add']}` | `{row['bytes']}` | {row['reason']} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- CPU address is a best-effort 16KB bank-window guess for debugger watching.",
        "- Low-confidence rows often contain control-like bytes and should not be patched from static evidence.",
        "- This queue supplements `manual_capture_queue.md`; it does not replace the v0.4 verification queue.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        "queued={queued_hits} high={high_confidence} medium={medium_confidence} low={low_confidence}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

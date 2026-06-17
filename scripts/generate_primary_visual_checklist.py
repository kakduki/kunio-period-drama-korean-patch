#!/usr/bin/env python3
"""Generate a focused visual checklist for rows already in the primary patch."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


PRIMARY_CONTENTS_JSON = REPO_ROOT / "rom_analysis" / "primary_patch_contents.json"
MANUAL_STATUS_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_status.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.md"


PRIMARY_ROM = "output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes"
WATCHER_LUA = "lua/kunio_manual_v042_capture_watch.lua"
SUMMARY_COMMAND = (
    "python scripts/analyze_manual_screen_dump.py "
    "--input-dir rom_analysis/manual_screen_dump_v042 "
    "--output rom_analysis/manual_screen_dump_v042/summary.md"
)


PRIORITY_BY_EVIDENCE = {
    "runtime-confirmed": 10,
    "encoding-exact": 20,
    "static-candidate+pointer": 30,
    "static-candidate": 40,
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_rom(value: object) -> str:
    text = str(value or "").replace("ROM+", "").strip()
    if text.lower().startswith("0x"):
        return f"0x{int(text, 16):05X}"
    return text


def status_by_rom() -> dict[str, dict[str, object]]:
    if not MANUAL_STATUS_JSON.exists():
        return {}
    data = load_json(MANUAL_STATUS_JSON)
    result = {}
    for card in data.get("cards", []):
        if isinstance(card, dict):
            result[normalize_rom(card.get("rom_hit"))] = card
    return result


def screen_hint(row: dict[str, object]) -> str:
    romaji = str(row.get("romaji", ""))
    if romaji == "Katana":
        return "look for a katana/weapon item label"
    if romaji == "Hashi":
        return "look for a bridge/stage/location label"
    if romaji == "Heishichi":
        return "look for a visible Heishichi name/dialogue context"
    if romaji == "Raifu":
        return "look for a life/status UI label"
    if romaji == "Tatsuichi":
        return "look for a visible Tatsuichi name/dialogue context"
    return "manually reach the exact text/menu/status screen"


def make_payload() -> dict[str, object]:
    contents = load_json(PRIMARY_CONTENTS_JSON)
    statuses = status_by_rom()
    rows = []
    for row in contents["applied_rows"]:
        rom_hit = normalize_rom(row["rom_hit"])
        evidence = str(row.get("evidence_level", ""))
        manual = statuses.get(rom_hit, {})
        priority = PRIORITY_BY_EVIDENCE.get(evidence, 90)
        rows.append(
            {
                "priority": priority,
                "rom_hit": rom_hit,
                "romaji": row.get("romaji", ""),
                "source_display": row.get("source_display", ""),
                "korean_display": row.get("korean_display", ""),
                "old_bytes": row.get("old_bytes", ""),
                "new_bytes": row.get("new_bytes", ""),
                "evidence_level": evidence,
                "manual_status": row.get("manual_status", ""),
                "screen_hint": screen_hint(row),
                "capture_status": manual.get("status", "not_in_manual_capture_cards"),
                "record_file_count": manual.get("record_file_count", 0),
                "matches": len(manual.get("matches", [])) if isinstance(manual.get("matches", []), list) else 0,
                "rom_to_open": PRIMARY_ROM,
                "watcher_lua": WATCHER_LUA,
                "summary_command": SUMMARY_COMMAND,
            }
        )

    rows.sort(key=lambda row: (int(row["priority"]), str(row["rom_hit"])))
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["capture_status"])] = counts.get(str(row["capture_status"]), 0) + 1

    return {
        "source": str(PRIMARY_CONTENTS_JSON.relative_to(REPO_ROOT)),
        "summary": {
            "row_count": len(rows),
            "primary_rom": PRIMARY_ROM,
            "watcher_lua": WATCHER_LUA,
            "status_counts": counts,
            "rule": "Verify already-applied v0.4.2 rows on the patched ROM before treating the IPS as release-ready.",
        },
        "rows": rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Primary Visual Checklist",
        "",
        "This is the short visual-review queue for text rows already changed by the primary IPS.",
        "",
        "## Summary",
        "",
        f"- Rows to visually verify: **{summary['row_count']}**",
        f"- Open patched ROM: `{summary['primary_rom']}`",
        f"- Run watcher once: `{summary['watcher_lua']}`",
        "- Press `D` only on a screen that visibly matches one of the rows below.",
        "",
        "| status | count |",
        "| --- | ---: |",
    ]
    for status, count in sorted(summary["status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")

    lines += [
        "",
        "## Priority Rows",
        "",
        "| priority | ROM | romaji | source | Korean | evidence | capture status | screen hint |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        source = row["source_display"] or "-"
        korean = row["korean_display"] or "-"
        lines.append(
            f"| {row['priority']} | `{row['rom_hit']}` | {row['romaji']} | {source} | {korean} | "
            f"`{row['evidence_level']}` | `{row['capture_status']}` | {row['screen_hint']} |"
        )

    lines += [
        "",
        "## Commands",
        "",
        "```text",
        WATCHER_LUA,
        "```",
        "",
        "```powershell",
        SUMMARY_COMMAND,
        "python scripts/generate_manual_capture_status.py",
        "python scripts/generate_primary_visual_checklist.py",
        "```",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"rows={payload['summary']['row_count']} statuses={payload['summary']['status_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

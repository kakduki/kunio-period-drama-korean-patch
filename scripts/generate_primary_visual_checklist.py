#!/usr/bin/env python3
"""Generate a focused visual checklist for rows already in the primary patch."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


PRIMARY_CONTENTS_JSON = REPO_ROOT / "rom_analysis" / "primary_patch_contents.json"
MANUAL_STATUS_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_status.json"
PRIMARY_REVIEW_JSON = REPO_ROOT / "rom_analysis" / "primary_visual_review.json"
AUTO_EXPLORER_SUMMARY_JSON = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "summary.json"
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


def visual_review_by_rom() -> dict[str, dict[str, object]]:
    if not PRIMARY_REVIEW_JSON.exists():
        return {}
    data = load_json(PRIMARY_REVIEW_JSON)
    result = {}
    for row in data.get("rows", []):
        if isinstance(row, dict):
            result[normalize_rom(row.get("rom_hit"))] = row
    return result


def auto_explorer_matches_by_rom() -> dict[str, list[dict[str, object]]]:
    if not AUTO_EXPLORER_SUMMARY_JSON.exists():
        return {}
    data = load_json(AUTO_EXPLORER_SUMMARY_JSON)
    result: dict[str, list[dict[str, object]]] = {}
    for match in data.get("active_matches", []):
        if not isinstance(match, dict):
            continue
        rom = normalize_rom(match.get("rom_hit"))
        result.setdefault(rom, []).append(match)
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
    reviews = visual_review_by_rom()
    auto_matches = auto_explorer_matches_by_rom()
    rows = []
    for row in contents["applied_rows"]:
        rom_hit = normalize_rom(row["rom_hit"])
        evidence = str(row.get("evidence_level", ""))
        manual = statuses.get(rom_hit, {})
        review = reviews.get(rom_hit, {})
        visual_confirmed = bool(review.get("visual_context_confirmed", False))
        priority = PRIORITY_BY_EVIDENCE.get(evidence, 90)
        capture_status = manual.get("status", "not_in_manual_capture_cards")
        auto_match_count = len(auto_matches.get(rom_hit, []))
        review_status = "visual_confirmed" if visual_confirmed else str(capture_status)
        if not visual_confirmed and auto_match_count:
            review_status = "auto_input_match_needs_visual"
        rows.append(
            {
                "priority": priority,
                "rom_hit": rom_hit,
                "romaji": row.get("romaji", ""),
                "meaning": row.get("meaning", ""),
                "source_display": row.get("source_display", ""),
                "korean_display": row.get("korean_display", ""),
                "old_bytes": row.get("old_bytes", ""),
                "new_bytes": row.get("new_bytes", ""),
                "evidence_level": evidence,
                "manual_status": row.get("manual_status", ""),
                "screen_hint": screen_hint(row),
                "capture_status": capture_status,
                "visual_context_confirmed": visual_confirmed,
                "screen_context": review.get("screen_context", ""),
                "reviewer_note": review.get("reviewer_note", ""),
                "review_status": review_status,
                "record_file_count": manual.get("record_file_count", 0),
                "matches": len(manual.get("matches", [])) if isinstance(manual.get("matches", []), list) else 0,
                "auto_input_match_count": auto_match_count,
                "auto_input_summary": str(AUTO_EXPLORER_SUMMARY_JSON.relative_to(REPO_ROOT)) if auto_match_count else "",
                "rom_to_open": PRIMARY_ROM,
                "watcher_lua": WATCHER_LUA,
                "summary_command": SUMMARY_COMMAND,
            }
        )

    rows.sort(key=lambda row: (int(row["priority"]), str(row["rom_hit"])))
    counts: dict[str, int] = {}
    visual_confirmed_count = 0
    auto_input_match_rows = 0
    for row in rows:
        counts[str(row["review_status"])] = counts.get(str(row["review_status"]), 0) + 1
        if row["visual_context_confirmed"]:
            visual_confirmed_count += 1
        if row["auto_input_match_count"]:
            auto_input_match_rows += 1

    return {
        "source": str(PRIMARY_CONTENTS_JSON.relative_to(REPO_ROOT)),
        "summary": {
            "row_count": len(rows),
            "visual_confirmed_count": visual_confirmed_count,
            "visual_pending_count": len(rows) - visual_confirmed_count,
            "auto_input_match_rows": auto_input_match_rows,
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
        f"- Visual confirmations: **{summary['visual_confirmed_count']}**",
        f"- Pending visual checks: **{summary['visual_pending_count']}**",
        f"- Auto-input byte-match rows: **{summary['auto_input_match_rows']}**",
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
        "| priority | ROM | romaji | human hint | source | Korean | evidence | auto matches | review status | screen hint |",
        "| ---: | --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        source = row["source_display"] or "-"
        korean = row["korean_display"] or "-"
        lines.append(
            f"| {row['priority']} | `{row['rom_hit']}` | {row['romaji']} | {row['meaning'] or '-'} | {source} | {korean} | "
            f"`{row['evidence_level']}` | {row['auto_input_match_count']} | `{row['review_status']}` | {row['screen_hint']} |"
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
        "python scripts/record_primary_visual_review.py 0x07227 --confirm --screen-context \"katana/weapon item label visible\"",
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

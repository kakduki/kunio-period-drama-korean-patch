#!/usr/bin/env python3
"""Generate a row-by-row v0.4.3 proof status report."""

from __future__ import annotations

import json
from pathlib import Path

from build_v043_from_broad_scan_proof import (
    DEFAULT_PROOF_PACKET,
    DEFAULT_REVIEW,
    DEFAULT_SUMMARY,
    normalize_rom,
    write_review_template,
)
from readable_labels import readable_for_romaji
from rom_utils import REPO_ROOT


BUILD_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.3_broad_verified_build_report.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "v043_proof_status.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "v043_proof_status.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def rows_by_rom(payload: dict[str, object], key: str) -> dict[str, dict[str, object]]:
    rows = {}
    for row in payload.get(key, []):
        if isinstance(row, dict) and row.get("rom_offset"):
            rows[normalize_rom(row["rom_offset"])] = row
    return rows


def status_for(cpu_match: bool, visual_confirmed: bool, applied: bool) -> str:
    if applied:
        return "applied"
    if cpu_match and visual_confirmed:
        return "ready_for_v043_builder"
    if cpu_match:
        return "needs_visual_review"
    if visual_confirmed:
        return "needs_cpu_read_match"
    return "needs_manual_capture"


def next_action_for(status: str, row: dict[str, object]) -> str:
    rom = row["rom_offset"]
    if status == "applied":
        return "Keep the generated v0.4.3 candidate and verify it on the matching screen."
    if status == "ready_for_v043_builder":
        return "Run `python scripts/build_v043_from_broad_scan_proof.py` to build the candidate."
    if status == "needs_visual_review":
        context = row.get("screen_hint") or "matching screen context"
        return f"Run `python scripts/record_visual_review.py {rom} --confirm --screen-context \"{context}\"` after checking the visible screen."
    if status == "needs_cpu_read_match":
        return "Run the base ROM, manually reach this screen, then run `lua/kunio_manual_broad_scan_dump.lua` and `python scripts/analyze_broad_scan_manual_dump.py`."
    return "Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context."


def make_payload() -> dict[str, object]:
    proof_packet = load_json(DEFAULT_PROOF_PACKET)
    write_review_template(DEFAULT_REVIEW, proof_packet)
    summary = load_json(DEFAULT_SUMMARY)
    review = load_json(DEFAULT_REVIEW)
    build_report = load_json(BUILD_REPORT)

    tasks = rows_by_rom(proof_packet, "tasks")
    cpu_matches = rows_by_rom(summary, "promotable_after_visual_review")
    reviews = rows_by_rom(review, "rows")
    applied = rows_by_rom(build_report, "applied")

    rows = []
    for rom, task in sorted(tasks.items()):
        review_row = reviews.get(rom, {})
        cpu_match = rom in cpu_matches
        visual_confirmed = review_row.get("visual_context_confirmed") is True
        applied_now = rom in applied
        readable = readable_for_romaji(task.get("romaji", ""))
        row = {
            "task": task.get("task"),
            "rom_offset": rom,
            "kind": task.get("kind", ""),
            "confidence": task.get("confidence", ""),
            "romaji": task.get("romaji", ""),
            "source_display": readable.get("source_display") or task.get("source_display") or task.get("source", ""),
            "korean_display": readable.get("korean_display") or task.get("korean_display") or task.get("korean", ""),
            "screen_hint": readable.get("screen_hint") or task.get("screen_hint", ""),
            "original_bytes": task.get("original_bytes", ""),
            "planned_prg_bytes": task.get("planned_prg_bytes", ""),
            "cpu_read_match_present": cpu_match,
            "visual_context_confirmed": visual_confirmed,
            "screen_context": review_row.get("screen_context", ""),
            "applied_in_v043_build": applied_now,
            "status": status_for(cpu_match, visual_confirmed, applied_now),
        }
        row["next_action"] = next_action_for(str(row["status"]), row)
        rows.append(row)

    counts = {}
    for row in rows:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1

    return {
        "source": {
            "proof_packet": rel(DEFAULT_PROOF_PACKET),
            "summary": rel(DEFAULT_SUMMARY),
            "visual_review": rel(DEFAULT_REVIEW),
            "build_report": rel(BUILD_REPORT),
        },
        "summary": {
            "rows": len(rows),
            "cpu_read_matches": sum(1 for row in rows if row["cpu_read_match_present"]),
            "visual_reviews_confirmed": sum(1 for row in rows if row["visual_context_confirmed"]),
            "applied_in_v043_build": sum(1 for row in rows if row["applied_in_v043_build"]),
            "status_counts": counts,
            "build_verdict": build_report.get("verdict", "missing"),
        },
        "rows": rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# v0.4.3 Proof Status",
        "",
        "This report joins the broad-scan proof packet, CPU-read summary, visual review file, and v0.4.3 build report.",
        "",
        "## Summary",
        "",
        f"- Rows: **{summary['rows']}**",
        f"- CPU-read matches: **{summary['cpu_read_matches']}**",
        f"- Visual reviews confirmed: **{summary['visual_reviews_confirmed']}**",
        f"- Applied in v0.4.3 build: **{summary['applied_in_v043_build']}**",
        f"- Build verdict: `{summary['build_verdict']}`",
        "",
        "## Rows",
        "",
        "| task | status | ROM | expected text | Korean | CPU read | visual | planned bytes | next action |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        cpu = "yes" if row["cpu_read_match_present"] else "no"
        visual = "yes" if row["visual_context_confirmed"] else "no"
        lines.append(
            f"| {row['task']} | `{row['status']}` | `{row['rom_offset']}` | {row['source_display']} | "
            f"{row['korean_display']} | {cpu} | {visual} | `{row['planned_prg_bytes']}` | {row['next_action']} |"
        )

    lines += [
        "",
        "## Status Meaning",
        "",
        "- `needs_manual_capture`: no CPU-read match and no visual confirmation yet.",
        "- `needs_visual_review`: CPU bytes matched; confirm the visible screen before building.",
        "- `needs_cpu_read_match`: visual review was marked, but the CPU-read proof is still missing.",
        "- `ready_for_v043_builder`: both gates are satisfied; run the v0.4.3 builder.",
        "- `applied`: the row was included in the generated v0.4.3 candidate.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "rows={rows} cpu={cpu_read_matches} visual={visual_reviews_confirmed} applied={applied_in_v043_build}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Summarize manual proof evidence for the three route-specific watchers."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


ROUTES_JSON = REPO_ROOT / "rom_analysis" / "route_fceux_targets.json"
BROAD_DUMP_DIR = REPO_ROOT / "rom_analysis" / "manual_screen_dump_broad_scan"
BROAD_SUMMARY_JSON = BROAD_DUMP_DIR / "summary.json"
BROAD_VISUAL_REVIEW_JSON = BROAD_DUMP_DIR / "visual_review.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "route_proof_status.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "route_proof_status.md"


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def normalize_rom(value: object) -> str:
    text = str(value or "").replace("ROM+", "").strip()
    if text.lower().startswith("0x"):
        return f"0x{int(text, 16):05X}"
    return text


def read_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def visual_review_by_label() -> dict[str, str]:
    review = load_json(BROAD_VISUAL_REVIEW_JSON)
    rows = review.get("reviews", []) or review.get("visual_reviews", []) or []
    result: dict[str, str] = {}
    for row in rows:
        if isinstance(row, dict):
            label = str(row.get("label", ""))
            verdict = str(row.get("verdict", "") or row.get("visual_verdict", ""))
            if label:
                result[label] = verdict
    return result


def target_matches() -> dict[str, list[dict[str, object]]]:
    matches: dict[str, list[dict[str, object]]] = {}
    for records_path in sorted(BROAD_DUMP_DIR.glob("manual_frame_*_target_records.tsv")):
        rows = read_records(records_path)
        frame = rows[0].get("frame", "?") if rows else "?"
        for row in rows:
            label = row.get("label", "")
            if not label:
                continue
            if row.get("active_expected_match", "").lower() != "true":
                continue
            matches.setdefault(label, []).append(
                {
                    "records": rel(records_path),
                    "frame": frame,
                    "rom_hit": normalize_rom(row.get("rom_hit", "")),
                    "cpu_range": row.get("cpu_range", ""),
                    "expected_bytes": row.get("expected_bytes", ""),
                    "record_snapshot": row.get("record_snapshot", ""),
                }
            )
    return matches


def route_status(route: dict[str, object], matches: dict[str, list[dict[str, object]]], reviews: dict[str, str]) -> dict[str, object]:
    target_rows = route["targets"]
    target_statuses = []
    matched_count = 0
    visual_confirmed_count = 0
    for target in target_rows:
        label = str(target["label"])
        target_match_rows = matches.get(label, [])
        verdict = reviews.get(label, "")
        if target_match_rows:
            matched_count += 1
        if verdict in {"confirmed", "pass", "accepted", "visual_confirmed"}:
            visual_confirmed_count += 1
        target_statuses.append(
            {
                "label": label,
                "rom_offset": target["rom_offset"],
                "cpu_start": f"0x{int(target['start']):04X}",
                "cpu_stop": f"0x{int(target['stop']):04X}",
                "match_count": len(target_match_rows),
                "visual_verdict": verdict,
                "matches": target_match_rows,
            }
        )

    if visual_confirmed_count == len(target_statuses):
        status = "route_visual_confirmed"
        next_step = "Promote this route's rows into the verified broad patch candidate."
    elif matched_count:
        status = "cpu_match_needs_visual_review"
        next_step = "Inspect the captured screen/PPU context, then record visual verdicts."
    elif sorted(BROAD_DUMP_DIR.glob("manual_frame_*_target_records.tsv")):
        status = "dump_exists_no_route_match"
        next_step = "The current dump is from the wrong screen for this route; run the route watcher on the listed context."
    else:
        status = "no_dump_records"
        next_step = "Do not keep blind autoplay running; manually reach this route's screen and press D in its route watcher."

    return {
        "route": route["route"],
        "group": route["group"],
        "watch_lua": route["watcher_lua"],
        "target_lua": route["target_lua"],
        "screen_hint": target_rows[0]["screen_hint"] if target_rows else "",
        "target_count": len(target_statuses),
        "matched_target_count": matched_count,
        "visual_confirmed_target_count": visual_confirmed_count,
        "status": status,
        "next_step": next_step,
        "targets": target_statuses,
    }


def make_payload() -> dict[str, object]:
    routes_payload = load_json(ROUTES_JSON)
    broad_summary = load_json(BROAD_SUMMARY_JSON)
    matches = target_matches()
    reviews = visual_review_by_label()
    routes = [route_status(route, matches, reviews) for route in routes_payload["routes"]]
    counts: dict[str, int] = {}
    for route in routes:
        counts[str(route["status"])] = counts.get(str(route["status"]), 0) + 1
    return {
        "source": rel(ROUTES_JSON),
        "manual_dump_summary": rel(BROAD_SUMMARY_JSON),
        "summary": {
            "route_count": len(routes),
            "target_count": sum(int(route["target_count"]) for route in routes),
            "matched_target_count": sum(int(route["matched_target_count"]) for route in routes),
            "visual_confirmed_target_count": sum(int(route["visual_confirmed_target_count"]) for route in routes),
            "status_counts": counts,
            "broad_dump_status": broad_summary.get("status", "missing_summary"),
            "rule": "Route proof needs a CPU-read byte match plus matching visible screen context; blind autoplay is not useful here.",
        },
        "routes": routes,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Route Proof Status",
        "",
        "This report turns the three route-specific FCEUX watchers into a short proof checklist.",
        "",
        "## Summary",
        "",
        f"- Routes: **{summary['route_count']}**",
        f"- Targets: **{summary['target_count']}**",
        f"- CPU-read matched targets: **{summary['matched_target_count']}**",
        f"- Visual-confirmed targets: **{summary['visual_confirmed_target_count']}**",
        f"- Broad dump status: `{summary['broad_dump_status']}`",
        "- Rule: CPU-read bytes plus visible screen context are both required before promotion.",
        "",
        "| route | group | status | targets | matched | visual | next step |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for route in payload["routes"]:
        lines.append(
            f"| {route['route']} | {route['group']} | `{route['status']}` | "
            f"{route['target_count']} | {route['matched_target_count']} | "
            f"{route['visual_confirmed_target_count']} | {route['next_step']} |"
        )

    lines += [
        "",
        "## Route Watchers",
        "",
    ]
    for route in payload["routes"]:
        lines += [
            f"### Route {route['route']}: {route['group']}",
            "",
            f"- Watch Lua: `{route['watch_lua']}`",
            f"- Target Lua: `{route['target_lua']}`",
            f"- Screen hint: {route['screen_hint']}",
            "",
            "| label | ROM | CPU range | matches | visual verdict |",
            "| --- | --- | --- | ---: | --- |",
        ]
        for target in route["targets"]:
            lines.append(
                f"| `{target['label']}` | `{target['rom_offset']}` | "
                f"`{target['cpu_start']}-{target['cpu_stop']}` | "
                f"{target['match_count']} | `{target['visual_verdict']}` |"
            )
        lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"routes={payload['summary']['route_count']} statuses={payload['summary']['status_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

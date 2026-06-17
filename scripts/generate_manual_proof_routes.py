#!/usr/bin/env python3
"""Group screen-proof candidates into the smallest useful manual capture routes."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from rom_utils import REPO_ROOT


READINESS_JSON = REPO_ROOT / "rom_analysis" / "batch46_text_readiness.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "manual_proof_routes.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "manual_proof_routes.md"


ROUTE_ORDER = {
    "Kajiya": 1,
    "Tatsuji": 2,
    "Heishichi": 3,
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def route_key(row: dict[str, object]) -> str:
    return str(row["romaji"] or row["screen_hint"])


def make_payload() -> dict[str, object]:
    readiness = load_json(READINESS_JSON)
    candidates = readiness["screen_proof_candidates"]
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in candidates:
        grouped[route_key(row)].append(row)

    routes = []
    for index, key in enumerate(sorted(grouped, key=lambda value: ROUTE_ORDER.get(value, 99)), start=1):
        rows = sorted(grouped[key], key=lambda row: int(str(row["rom_offset"]), 16))
        offsets = [row["rom_offset"] for row in rows]
        planned_byte_sets = sorted({" ".join(row["planned_prg_bytes_after_batch46"]) for row in rows})
        routes.append(
            {
                "route": index,
                "group": key,
                "candidate_count": len(rows),
                "rom_offsets": offsets,
                "planned_prg_byte_sets": planned_byte_sets,
                "confidence_levels": sorted({str(row["confidence"]) for row in rows}),
                "screen_hint": rows[0]["screen_hint"],
                "rom_to_open": "rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes",
                "capture_lua": "lua/kunio_manual_broad_scan_dump.lua",
                "summary_command": "python scripts/analyze_broad_scan_manual_dump.py",
                "decision_rule": "Promote only rows with both CPU-read matches and matching visible screen context.",
                "candidates": rows,
            }
        )

    return {
        "source": str(READINESS_JSON.relative_to(REPO_ROOT)),
        "summary": {
            "candidate_count": len(candidates),
            "route_count": len(routes),
            "groups": [route["group"] for route in routes],
            "rule": "Use one manually reached screen/context per route group when possible; do not extend blind autoplay.",
        },
        "routes": routes,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Manual Proof Routes",
        "",
        "This groups the current screen-proof candidates by likely manual capture context, so the next verification pass can avoid one task per offset.",
        "",
        "## Summary",
        "",
        f"- Screen-proof candidates: **{summary['candidate_count']}**",
        f"- Manual route groups: **{summary['route_count']}**",
        f"- Groups: **{', '.join(summary['groups'])}**",
        "",
        "## Routes",
        "",
    ]
    for route in payload["routes"]:
        lines += [
            f"### Route {route['route']}: {route['group']}",
            "",
            f"- Candidate offsets: `{', '.join(route['rom_offsets'])}`",
            f"- Planned byte sets: `{'; '.join(route['planned_prg_byte_sets'])}`",
            f"- Screen hint: {route['screen_hint']}",
            f"- Open ROM: `{route['rom_to_open']}`",
            f"- Run Lua: `{route['capture_lua']}`",
            f"- Summarize: `{route['summary_command']}`",
            "",
            "| ROM | confidence | source bytes | planned bytes |",
            "| --- | --- | ---: | --- |",
        ]
        for row in route["candidates"]:
            lines.append(
                f"| `{row['rom_offset']}` | {row['confidence']} | {row['source_byte_len']} | "
                f"`{' '.join(row['planned_prg_bytes_after_batch46'])}` |"
            )
        lines.append("")

    lines += [
        "## Rule",
        "",
        "- Capture on the base Japanese ROM for these broad-scan proof routes.",
        "- One route may produce evidence for more than one offset, but each promoted row still needs its own CPU-read match.",
        "- If a route only shows the title/opening screen or no target text, stop and switch route instead of extending autoplay.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "routes={route_count} candidates={candidate_count} groups={groups}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

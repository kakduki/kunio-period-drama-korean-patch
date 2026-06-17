#!/usr/bin/env python3
"""Generate the single next manual FCEUX run queue."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


PRIMARY_VISUAL_JSON = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
ROUTE_PROOF_JSON = REPO_ROOT / "rom_analysis" / "route_proof_status.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "next_manual_run.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def primary_actions(primary: dict[str, object]) -> list[dict[str, object]]:
    actions = []
    for row in primary["rows"]:
        if row.get("matches") or row.get("capture_status") not in {"not_in_manual_capture_cards", "no_dump_records"}:
            continue
        actions.append(
            {
                "phase": "primary_v042_visual_review",
                "priority": int(row["priority"]),
                "rom_to_open": row["rom_to_open"],
                "watcher_lua": row["watcher_lua"],
                "target": row["rom_hit"],
                "group": row["romaji"],
                "screen_hint": row["screen_hint"],
                "why": "This row is already changed by the primary IPS, so visual review moves the current patch closer to release-readiness.",
                "after_capture": [
                    "python scripts/refresh_after_manual_capture.py --phase primary",
                ],
            }
        )
    return actions


def route_actions(route_status: dict[str, object]) -> list[dict[str, object]]:
    actions = []
    for route in route_status["routes"]:
        if route.get("status") != "no_dump_records":
            continue
        route_priority = 100 + int(route["route"])
        actions.append(
            {
                "phase": "v043_candidate_proof",
                "priority": route_priority,
                "rom_to_open": "rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes",
                "watcher_lua": route["watch_lua"],
                "target": ", ".join(target["rom_offset"] for target in route["targets"]),
                "group": route["group"],
                "screen_hint": route["screen_hint"],
                "why": "This route can unlock additional v0.4.3 text rows, but it needs base-ROM CPU-read and visual screen proof.",
                "after_capture": [
                    "python scripts/refresh_after_manual_capture.py --phase broad",
                ],
            }
        )
    return actions


def make_payload() -> dict[str, object]:
    primary = load_json(PRIMARY_VISUAL_JSON)
    route_status = load_json(ROUTE_PROOF_JSON)
    actions = primary_actions(primary) + route_actions(route_status)
    actions.sort(key=lambda row: (int(row["priority"]), str(row["phase"])))
    next_action = actions[0] if actions else None
    return {
        "source": {
            "primary_visual_checklist": str(PRIMARY_VISUAL_JSON.relative_to(REPO_ROOT)),
            "route_proof_status": str(ROUTE_PROOF_JSON.relative_to(REPO_ROOT)),
        },
        "summary": {
            "action_count": len(actions),
            "primary_visual_pending": len([row for row in actions if row["phase"] == "primary_v042_visual_review"]),
            "route_proof_pending": len([row for row in actions if row["phase"] == "v043_candidate_proof"]),
            "recommended_phase": next_action["phase"] if next_action else "none",
            "rule": "Verify already-applied primary rows first; then gather base-ROM route proof for new text candidates.",
        },
        "next_action": next_action,
        "actions": actions,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    next_action = payload["next_action"]
    lines = [
        "# Next Manual Run",
        "",
        "This is the shortest current FCEUX action queue. It combines primary-patch visual review and v0.4.3 route proof work.",
        "",
        "## Summary",
        "",
        f"- Pending actions: **{summary['action_count']}**",
        f"- Primary v0.4.2 visual checks: **{summary['primary_visual_pending']}**",
        f"- v0.4.3 route proof checks: **{summary['route_proof_pending']}**",
        f"- Recommended phase: `{summary['recommended_phase']}`",
        "- Rule: verify already-applied rows first, then prove new route candidates.",
        "",
    ]
    if next_action:
        lines += [
            "## Recommended Next Action",
            "",
            f"- Open ROM: `{next_action['rom_to_open']}`",
            f"- Run Lua: `{next_action['watcher_lua']}`",
            f"- Target: `{next_action['target']}`",
            f"- Group: `{next_action['group']}`",
            f"- Screen hint: {next_action['screen_hint']}",
            f"- Why: {next_action['why']}",
            "- If the visible screen is still the title/opening screen, stop with `Q` and manually change screens.",
            "",
            "After capture:",
            "",
            "```powershell",
        ]
        lines.extend(next_action["after_capture"])
        lines += [
            "```",
            "",
        ]

    lines += [
        "## Full Queue",
        "",
        "| priority | phase | target | group | ROM | watcher | hint |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["actions"]:
        lines.append(
            f"| {row['priority']} | `{row['phase']}` | `{row['target']}` | {row['group']} | "
            f"`{row['rom_to_open']}` | `{row['watcher_lua']}` | {row['screen_hint']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "actions={action_count} primary={primary_visual_pending} routes={route_proof_pending}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

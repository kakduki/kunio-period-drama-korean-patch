#!/usr/bin/env python3
"""Generate a focused action plan from the current release gate status."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


RELEASE_GATE_JSON = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_checklist.json"
NEXT_MANUAL_RUN_JSON = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
HIGH_RISK_CANDIDATES = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "high_risk_candidates.csv"
PADDING_MATRIX = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "padding_experiment_matrix.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_action_plan.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_action_plan.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def make_payload() -> dict[str, object]:
    gate = load_json(RELEASE_GATE_JSON)
    next_manual = load_json(NEXT_MANUAL_RUN_JSON)
    high_risk_rows = load_csv(HIGH_RISK_CANDIDATES)
    padding = load_json(PADDING_MATRIX)
    gate_rows = gate.get("gates", [])
    open_gates = [row for row in gate_rows if row.get("status") in {"FAIL", "UNKNOWN"}]
    next_action = next_manual.get("next_action") if isinstance(next_manual.get("next_action"), dict) else {}
    padding_v05 = [
        row for row in padding.get("rows", [])
        if row.get("experiment_set") == "v05-current-font-base"
    ]

    actions: list[dict[str, object]] = []
    for row in open_gates:
        gate_name = str(row.get("gate", ""))
        if gate_name == "release-included visual proof":
            actions.append(
                {
                    "priority": 10,
                    "gate": gate_name,
                    "status": row["status"],
                    "failure_class": row["failure_class"],
                    "action": "Run the current primary visual-review queue and record a visible matching screen.",
                    "target": next_action.get("target", ""),
                    "phase": next_action.get("phase", "primary_v042_visual_review"),
                    "rom_to_open": next_action.get("rom_to_open", ""),
                    "watcher_lua": next_action.get("watcher_lua", ""),
                    "command": next_action.get("record_visual_review", ""),
                    "refresh": "; ".join(next_action.get("after_capture", [])),
                    "evidence_needed": "visible-screen capture and primary visual review confirmation",
                }
            )
        elif gate_name == "high-risk/quarantined visual proof":
            actions.append(
                {
                    "priority": 20,
                    "gate": gate_name,
                    "status": row["status"],
                    "failure_class": row["failure_class"],
                    "action": "Collect item-list visual proof before merging any quarantined Katana candidate.",
                    "target": ", ".join(candidate["rom_offset"] for candidate in high_risk_rows),
                    "phase": "katana_quarantine_visual_proof",
                    "rom_to_open": "output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes",
                    "watcher_lua": "lua/kunio_manual_v042_capture_watch.lua",
                    "command": "python scripts/record_primary_visual_review.py 0x07227 --confirm --screen-context \"katana/weapon item label visible\"",
                    "refresh": "python scripts/refresh_after_manual_capture.py --phase primary",
                    "evidence_needed": "Katana/item-list screen where the intended row is visibly readable",
                }
            )
        elif gate_name == "shortened padding rule acceptance":
            actions.append(
                {
                    "priority": 30,
                    "gate": gate_name,
                    "status": row["status"],
                    "failure_class": row["failure_class"],
                    "action": "Do not promote shortened replacements until one padding strategy has strict PPU or visual acceptance.",
                    "target": "ROM+0x071A4 Chikara -> 힘",
                    "phase": "padding_rule_acceptance",
                    "rom_to_open": "output/kunio_period_drama_korean_prg_padding_exp_v05_<strategy>.nes",
                    "watcher_lua": "lua/kunio_auto_dump.lua",
                    "command": "python scripts/audit_padding_experiment_pipeline.py",
                    "refresh": "python scripts/generate_patch_progress_dashboard.py",
                    "evidence_needed": f"strict PPU/visual acceptance for one of {len(padding_v05)} v05 padding strategies",
                }
            )
    actions.sort(key=lambda action: int(action["priority"]))
    return {
        "source": {
            "release_gate_checklist": rel(RELEASE_GATE_JSON),
            "next_manual_run": rel(NEXT_MANUAL_RUN_JSON),
            "high_risk_candidates": rel(HIGH_RISK_CANDIDATES),
            "padding_experiment_matrix": rel(PADDING_MATRIX),
        },
        "summary": {
            "open_gate_count": len(open_gates),
            "action_count": len(actions),
            "next_priority": actions[0]["priority"] if actions else None,
            "next_gate": actions[0]["gate"] if actions else "none",
            "release_ready": gate.get("summary", {}).get("release_ready", False),
        },
        "actions": actions,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Release Gate Action Plan",
        "",
        "This queue is generated from `release_gate_checklist.json`. It converts open FAIL/UNKNOWN gates into the next concrete evidence tasks.",
        "",
        "## Summary",
        "",
        f"- Open gates: **{summary['open_gate_count']}**",
        f"- Actions: **{summary['action_count']}**",
        f"- Next gate: `{summary['next_gate']}`",
        f"- Release ready: `{summary['release_ready']}`",
        "",
        "## Actions",
        "",
        "| priority | gate | status | failure class | phase | target | evidence needed | command |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["actions"]:
        lines.append(
            f"| {row['priority']} | {row['gate']} | {row['status']} | {row['failure_class']} | "
            f"`{row['phase']}` | `{row['target']}` | {row['evidence_needed']} | `{row['command']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print("actions={action_count} next={next_gate}".format(**payload["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

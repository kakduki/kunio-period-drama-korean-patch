#!/usr/bin/env python3
"""Generate a one-page progress dashboard for the Korean patch."""

from __future__ import annotations

import json
import csv
from pathlib import Path

from rom_utils import REPO_ROOT


PRIMARY_CONTENTS = REPO_ROOT / "rom_analysis" / "primary_patch_contents.json"
NEXT_MANUAL_RUN = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
CURRENT_PRIMARY_VISUAL_TASK = REPO_ROOT / "rom_analysis" / "current_primary_visual_task.json"
PRIMARY_VISUAL = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
AUTO_INPUT_EVIDENCE = REPO_ROOT / "rom_analysis" / "auto_input_evidence_report.json"
AUTO_INPUT_TRIAGE = REPO_ROOT / "rom_analysis" / "auto_input_visual_triage.json"
KATANA_EXPLORER = REPO_ROOT / "rom_analysis" / "katana_visual_explorer_v042" / "report.json"
KATANA_SLOT_CANDIDATES = REPO_ROOT / "rom_analysis" / "katana_inventory_slot_candidates.json"
KATANA_ITEMLIST_STATE_PROBE_NOTES = REPO_ROOT / "rom_analysis" / "katana_itemlist_state_probe_v042_early_notes.md"
KATANA_AUTOPLAY_ROUTE_CAPTURE_NOTES = REPO_ROOT / "rom_analysis" / "katana_autoplay_route_capture_v042_notes.md"
V043_STATUS = REPO_ROOT / "rom_analysis" / "v043_proof_status.json"
MANUAL_DUMP_INVENTORY = REPO_ROOT / "rom_analysis" / "manual_dump_inventory.json"
CANDIDATE_COMBINED_REPORT = REPO_ROOT / "output" / "kunio_period_drama_softgate_dev_combined_report.json"
HIGH_RISK_CANDIDATES = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "high_risk_candidates.csv"
PADDING_EXPERIMENT_MATRIX = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "padding_experiment_matrix.json"
PADDING_STRATEGY_PRIORITY = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "padding_strategy_priority.json"
RELEASE_GATE_JSON = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_checklist.json"
RELEASE_GATE_ACTION_PLAN = REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_action_plan.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "patch_progress_dashboard.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "patch_progress_dashboard.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def portable(value: object) -> object:
    if isinstance(value, str):
        return value.replace("\\", "/")
    return value


def make_payload() -> dict[str, object]:
    primary = load_json(PRIMARY_CONTENTS)
    next_run = load_json(NEXT_MANUAL_RUN)
    current_visual_task = load_json(CURRENT_PRIMARY_VISUAL_TASK)
    visual = load_json(PRIMARY_VISUAL)
    auto_input = load_json(AUTO_INPUT_EVIDENCE)
    auto_triage = load_json(AUTO_INPUT_TRIAGE)
    katana = load_json(KATANA_EXPLORER)
    katana_slots = load_json(KATANA_SLOT_CANDIDATES)
    v043 = load_json(V043_STATUS)
    inventory = load_json(MANUAL_DUMP_INVENTORY)
    candidate_combined = load_json(CANDIDATE_COMBINED_REPORT)
    high_risk_rows = load_csv(HIGH_RISK_CANDIDATES)
    padding_matrix = load_json(PADDING_EXPERIMENT_MATRIX)
    padding_priority = load_json(PADDING_STRATEGY_PRIORITY)
    release_gate = load_json(RELEASE_GATE_JSON)
    release_gate_action_plan = load_json(RELEASE_GATE_ACTION_PLAN)

    primary_summary = primary["summary"]
    next_summary = next_run["summary"]
    v043_summary = v043["summary"]
    next_action = next_run.get("next_action")

    blockers = []
    if next_summary.get("primary_visual_pending", 0):
        blockers.append("Primary v0.4.2 rows still need visible-screen review.")
    if v043_summary.get("cpu_read_matches", 0) == 0:
        blockers.append("v0.4.3 candidates have no base-ROM CPU-read proof yet.")
    if v043_summary.get("visual_reviews_confirmed", 0) == 0:
        blockers.append("v0.4.3 candidates have no visual-context confirmations yet.")
    if inventory["summary"].get("total_record_files", 0) == 0:
        blockers.append("No checked-in manual FCEUX dump records exist yet.")
    if high_risk_rows:
        blockers.append("High-risk/quarantined candidates require visual proof before dev/release merge.")
    if not padding_matrix["summary"].get("any_ppu_exact_pass", False):
        blockers.append("Shortened padding-rule candidates have CPU evidence but no strict PPU/visual acceptance yet.")

    padding_v05 = [
        row for row in padding_matrix.get("rows", [])
        if row.get("experiment_set") == "v05-current-font-base"
    ]
    padding_v05_cpu_pass = sum(1 for row in padding_v05 if row.get("cpu_active_status") == "PASS")
    padding_v05_ppu_pass = sum(1 for row in padding_v05 if row.get("ppu_exact_status") == "PASS")
    release_gate_rows = release_gate.get("gates", [])
    release_gate_failures = [row for row in release_gate_rows if row.get("status") == "FAIL"]
    release_gate_unknowns = [row for row in release_gate_rows if row.get("status") == "UNKNOWN"]

    return {
        "source": {
            "primary_patch_contents": rel(PRIMARY_CONTENTS),
            "next_manual_run": rel(NEXT_MANUAL_RUN),
            "current_primary_visual_task": rel(CURRENT_PRIMARY_VISUAL_TASK),
            "primary_visual_checklist": rel(PRIMARY_VISUAL),
            "auto_input_evidence_report": rel(AUTO_INPUT_EVIDENCE),
            "auto_input_visual_triage": rel(AUTO_INPUT_TRIAGE),
            "katana_visual_explorer": rel(KATANA_EXPLORER),
            "katana_inventory_slot_candidates": rel(KATANA_SLOT_CANDIDATES),
            "katana_itemlist_state_probe_notes": rel(KATANA_ITEMLIST_STATE_PROBE_NOTES),
            "katana_autoplay_route_capture_notes": rel(KATANA_AUTOPLAY_ROUTE_CAPTURE_NOTES),
            "v043_proof_status": rel(V043_STATUS),
            "manual_dump_inventory": rel(MANUAL_DUMP_INVENTORY),
            "candidate_combined_report": rel(CANDIDATE_COMBINED_REPORT),
            "high_risk_candidates": rel(HIGH_RISK_CANDIDATES),
            "padding_experiment_matrix": rel(PADDING_EXPERIMENT_MATRIX),
            "padding_strategy_priority": rel(PADDING_STRATEGY_PRIORITY),
            "release_gate_checklist": rel(RELEASE_GATE_JSON),
            "release_gate_action_plan": rel(RELEASE_GATE_ACTION_PLAN),
        },
        "summary": {
            "primary_candidate": primary_summary["primary_candidate"],
            "primary_ips": portable(primary_summary["primary_ips"]),
            "primary_expected_md5": primary_summary["primary_candidate_md5"],
            "primary_applied_rows": primary_summary["applied_count"],
            "primary_runtime_confirmed_rows": primary_summary["runtime_confirmed_count"],
            "primary_static_candidate_rows": primary_summary["static_candidate_count"],
            "pending_manual_actions": next_summary["action_count"],
            "pending_primary_visual_checks": next_summary["primary_visual_pending"],
            "pending_v043_route_proofs": next_summary["route_proof_pending"],
            "current_visual_task_decision": current_visual_task["summary"].get("decision", ""),
            "current_visual_task_context_status": current_visual_task["summary"].get("auto_input_context_status", ""),
            "current_visual_task_required_screen": current_visual_task["summary"].get("required_screen", ""),
            "primary_auto_input_match_rows": visual["summary"].get("auto_input_match_rows", 0),
            "auto_input_latest_png": auto_input["summary"].get("latest_png_review_image", ""),
            "auto_input_matched_primary_rows": auto_input["summary"].get("matched_primary_rows", 0),
            "auto_input_visual_approvals": auto_triage["summary"].get("visual_approval_rows", 0),
            "auto_input_triage_decision": auto_triage["summary"].get("decision", ""),
            "katana_item_list_frame": katana["summary"].get("item_list_frame", ""),
            "katana_active_match_on_item_list": katana["summary"].get("katana_active_match_on_item_list", ""),
            "katana_next_step": katana["summary"].get("next_step", ""),
            "katana_slot_candidate_counts": katana_slots["summary"].get("classification_counts", {}),
            "katana_slot_next_probe": katana_slots["summary"].get("recommended_next_probe", ""),
            "katana_itemlist_state_probe": "VISUAL_FAIL_ITEMLIST_EMPTY"
            if KATANA_ITEMLIST_STATE_PROBE_NOTES.exists()
            else "NOT_RUN",
            "katana_autoplay_route_capture": "VISUAL_FAIL_WRONG_CONTEXT"
            if KATANA_AUTOPLAY_ROUTE_CAPTURE_NOTES.exists()
            else "NOT_RUN",
            "v043_rows": v043_summary["rows"],
            "v043_cpu_read_matches": v043_summary["cpu_read_matches"],
            "v043_visual_confirmations": v043_summary["visual_reviews_confirmed"],
            "v043_applied_rows": v043_summary["applied_in_v043_build"],
            "manual_dump_record_files": inventory["summary"]["total_record_files"],
            "softgate_dev_combined_status": candidate_combined["build_status"],
            "softgate_dev_combined_strings": candidate_combined["applied_count"],
            "softgate_dev_combined_md5": candidate_combined["candidate_md5"],
            "softgate_dev_combined_rom": portable(candidate_combined["candidate_rom"]),
            "softgate_dev_combined_ips": portable(candidate_combined["candidate_ips"]),
            "quarantined_candidate_count": len(high_risk_rows),
            "quarantined_build_pass_count": sum(1 for row in high_risk_rows if row.get("build_status") == "PASS"),
            "quarantined_smoke_pass_count": sum(1 for row in high_risk_rows if row.get("boot_smoke") == "PASS"),
            "padding_v05_strategy_count": len(padding_v05),
            "padding_v05_cpu_pass_count": padding_v05_cpu_pass,
            "padding_v05_ppu_pass_count": padding_v05_ppu_pass,
            "padding_recommended_strategy": padding_priority.get("summary", {}).get("recommended_strategy", ""),
            "padding_recommended_risk_class": padding_priority.get("summary", {}).get("recommended_risk_class", ""),
            "padding_v05_decisions": sorted({row.get("decision", "") for row in padding_v05 if row.get("decision")}),
            "release_gate_status_counts": release_gate.get("summary", {}).get("status_counts", {}),
            "release_gate_failures": [row.get("gate", "") for row in release_gate_failures],
            "release_gate_unknowns": [row.get("gate", "") for row in release_gate_unknowns],
            "release_gate_action_count": release_gate_action_plan.get("summary", {}).get("action_count", 0),
            "release_gate_next_action": release_gate_action_plan.get("summary", {}).get("next_gate", "none"),
            "release_ready": release_gate.get("summary", {}).get("release_ready", False),
            "release_blockers": blockers,
        },
        "next_action": next_action,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    next_action = payload["next_action"]
    lines = [
        "# Patch Progress Dashboard",
        "",
        "Single-page status for the current Korean patch work.",
        "",
        "## Current Patch",
        "",
        f"- Primary candidate: **{summary['primary_candidate']}**",
        f"- Primary IPS: `{summary['primary_ips']}`",
        f"- Expected patched MD5: `{summary['primary_expected_md5']}`",
        f"- Applied text rows: **{summary['primary_applied_rows']}**",
        f"- Runtime-confirmed rows: **{summary['primary_runtime_confirmed_rows']}**",
        f"- Static candidate rows: **{summary['primary_static_candidate_rows']}**",
        "",
        "## Manual Evidence",
        "",
        f"- Pending manual actions: **{summary['pending_manual_actions']}**",
        f"- Pending primary visual checks: **{summary['pending_primary_visual_checks']}**",
        f"- Pending v0.4.3 route proofs: **{summary['pending_v043_route_proofs']}**",
        f"- Current visual task decision: `{summary['current_visual_task_decision']}`",
        f"- Current visual task context: `{summary['current_visual_task_context_status']}`",
        f"- Current visual task required screen: {summary['current_visual_task_required_screen']}",
        f"- Checked-in manual dump record files: **{summary['manual_dump_record_files']}**",
        f"- Auto-input byte-match rows: **{summary['primary_auto_input_match_rows']}**",
        f"- Auto-input matched primary rows: **{summary['auto_input_matched_primary_rows']}**",
        f"- Auto-input visual approvals: **{summary['auto_input_visual_approvals']}**",
        f"- Auto-input review image: `{summary['auto_input_latest_png']}`",
        f"- Auto-input triage: {summary['auto_input_triage_decision']}",
        f"- Katana item-list route frame: **{summary['katana_item_list_frame']}**",
        f"- Katana active on item-list screen: `{summary['katana_active_match_on_item_list']}`",
        f"- Katana next step: {summary['katana_next_step']}",
        f"- Katana slot next probe: {summary['katana_slot_next_probe']}",
        f"- Katana item-list state probe: `{summary['katana_itemlist_state_probe']}`",
        f"- Katana autoplay-route capture: `{summary['katana_autoplay_route_capture']}`",
        "",
        "## Candidate Pipeline",
        "",
        f"- Softgate dev combined: **{summary['softgate_dev_combined_strings']} strings**, `{summary['softgate_dev_combined_status']}`",
        f"- Softgate dev ROM: `{summary['softgate_dev_combined_rom']}`",
        f"- Softgate dev IPS: `{summary['softgate_dev_combined_ips']}`",
        f"- Softgate dev MD5: `{summary['softgate_dev_combined_md5']}`",
        f"- Quarantined candidates: **{summary['quarantined_candidate_count']}**",
        f"- Quarantined build PASS: **{summary['quarantined_build_pass_count']}**",
        f"- Quarantined smoke PASS: **{summary['quarantined_smoke_pass_count']}**",
        f"- Padding v05 strategies: **{summary['padding_v05_strategy_count']}**",
        f"- Padding v05 CPU PASS: **{summary['padding_v05_cpu_pass_count']}**",
        f"- Padding v05 strict PPU PASS: **{summary['padding_v05_ppu_pass_count']}**",
        f"- Padding recommended strategy: `{summary['padding_recommended_strategy']}`",
        f"- Padding recommended risk: `{summary['padding_recommended_risk_class']}`",
        f"- Padding decisions: `{', '.join(summary['padding_v05_decisions']) or 'none'}`",
        "",
        "## Release Gate",
        "",
        f"- Ready: `{summary['release_ready']}`",
        f"- Gate status counts: `{summary['release_gate_status_counts']}`",
        f"- Failing gates: `{', '.join(summary['release_gate_failures']) or 'none'}`",
        f"- Unknown gates: `{', '.join(summary['release_gate_unknowns']) or 'none'}`",
        f"- Action plan items: **{summary['release_gate_action_count']}**",
        f"- Next gate action: `{summary['release_gate_next_action']}`",
        "",
        "## v0.4.3 Gate",
        "",
        f"- Candidate rows: **{summary['v043_rows']}**",
        f"- CPU-read matches: **{summary['v043_cpu_read_matches']}**",
        f"- Visual confirmations: **{summary['v043_visual_confirmations']}**",
        f"- Applied rows: **{summary['v043_applied_rows']}**",
        "",
        "## Next Action",
        "",
    ]
    if isinstance(next_action, dict):
        lines += [
            f"- Phase: `{next_action['phase']}`",
            f"- Target: `{next_action['target']}`",
            f"- Group: `{next_action['group']}`",
            f"- ROM: `{next_action['rom_to_open']}`",
            f"- Lua: `{next_action['watcher_lua']}`",
            f"- Hint: {next_action['screen_hint']}",
            "- After capture:",
        ]
        lines.extend(f"  - `{command}`" for command in next_action.get("after_capture", []))
    else:
        lines.append("- None.")

    lines += [
        "",
        "## Release Blockers",
        "",
    ]
    for blocker in summary["release_blockers"]:
        lines.append(f"- {blocker}")
    lines += [
        "",
        "## Useful Commands",
        "",
        "```powershell",
        "python scripts/preflight_release_gate_action.py",
        "python scripts/preflight_manual_fceux.py",
        "python scripts/generate_current_primary_visual_task.py",
        "python scripts/run_next_manual_fceux.py",
        "python scripts/confirm_next_primary_visual.py --confirm-visible",
        "python scripts/prepare_next_manual_run.py --powershell",
        "python scripts/refresh_after_manual_capture.py --phase primary",
        "python scripts/refresh_after_manual_capture.py --phase broad",
        "python scripts/run_project_checks.py",
        "```",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(
        "pending={pending_manual_actions} primary={pending_primary_visual_checks} routes={pending_v043_route_proofs}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

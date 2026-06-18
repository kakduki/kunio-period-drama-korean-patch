#!/usr/bin/env python3
"""Generate a one-page progress dashboard for the Korean patch."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


PRIMARY_CONTENTS = REPO_ROOT / "rom_analysis" / "primary_patch_contents.json"
NEXT_MANUAL_RUN = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
PRIMARY_VISUAL = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
AUTO_INPUT_EVIDENCE = REPO_ROOT / "rom_analysis" / "auto_input_evidence_report.json"
V043_STATUS = REPO_ROOT / "rom_analysis" / "v043_proof_status.json"
MANUAL_DUMP_INVENTORY = REPO_ROOT / "rom_analysis" / "manual_dump_inventory.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "patch_progress_dashboard.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "patch_progress_dashboard.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def make_payload() -> dict[str, object]:
    primary = load_json(PRIMARY_CONTENTS)
    next_run = load_json(NEXT_MANUAL_RUN)
    visual = load_json(PRIMARY_VISUAL)
    auto_input = load_json(AUTO_INPUT_EVIDENCE)
    v043 = load_json(V043_STATUS)
    inventory = load_json(MANUAL_DUMP_INVENTORY)

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

    return {
        "source": {
            "primary_patch_contents": rel(PRIMARY_CONTENTS),
            "next_manual_run": rel(NEXT_MANUAL_RUN),
            "primary_visual_checklist": rel(PRIMARY_VISUAL),
            "auto_input_evidence_report": rel(AUTO_INPUT_EVIDENCE),
            "v043_proof_status": rel(V043_STATUS),
            "manual_dump_inventory": rel(MANUAL_DUMP_INVENTORY),
        },
        "summary": {
            "primary_candidate": primary_summary["primary_candidate"],
            "primary_ips": primary_summary["primary_ips"],
            "primary_expected_md5": primary_summary["primary_candidate_md5"],
            "primary_applied_rows": primary_summary["applied_count"],
            "primary_runtime_confirmed_rows": primary_summary["runtime_confirmed_count"],
            "primary_static_candidate_rows": primary_summary["static_candidate_count"],
            "pending_manual_actions": next_summary["action_count"],
            "pending_primary_visual_checks": next_summary["primary_visual_pending"],
            "pending_v043_route_proofs": next_summary["route_proof_pending"],
            "primary_auto_input_match_rows": visual["summary"].get("auto_input_match_rows", 0),
            "auto_input_latest_png": auto_input["summary"].get("latest_png_review_image", ""),
            "auto_input_matched_primary_rows": auto_input["summary"].get("matched_primary_rows", 0),
            "v043_rows": v043_summary["rows"],
            "v043_cpu_read_matches": v043_summary["cpu_read_matches"],
            "v043_visual_confirmations": v043_summary["visual_reviews_confirmed"],
            "v043_applied_rows": v043_summary["applied_in_v043_build"],
            "manual_dump_record_files": inventory["summary"]["total_record_files"],
            "release_ready": False,
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
        f"- Checked-in manual dump record files: **{summary['manual_dump_record_files']}**",
        f"- Auto-input byte-match rows: **{summary['primary_auto_input_match_rows']}**",
        f"- Auto-input matched primary rows: **{summary['auto_input_matched_primary_rows']}**",
        f"- Auto-input review image: `{summary['auto_input_latest_png']}`",
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
        "python scripts/preflight_manual_fceux.py",
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

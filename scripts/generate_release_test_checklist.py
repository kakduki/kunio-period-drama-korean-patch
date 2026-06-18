#!/usr/bin/env python3
"""Generate a concise manual test checklist for the current IPS bundle."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


MANIFEST_JSON = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"
REFERENCE_PLAN_JSON = REPO_ROOT / "rom_analysis" / "reference_capture_plan.json"
PRIMARY_VISUAL_JSON = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
PROOF_STATUS_JSON = REPO_ROOT / "rom_analysis" / "v043_proof_status.json"
ROUTE_TARGETS_JSON = REPO_ROOT / "rom_analysis" / "route_fceux_targets.json"
ROUTE_PROOF_STATUS_JSON = REPO_ROOT / "rom_analysis" / "route_proof_status.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "release_test_checklist.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "release_test_checklist.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def make_payload() -> dict[str, object]:
    manifest = load_json(MANIFEST_JSON)
    reference = load_json(REFERENCE_PLAN_JSON)
    primary_visual = load_json(PRIMARY_VISUAL_JSON)
    proof = load_json(PROOF_STATUS_JSON)
    route_targets = load_json(ROUTE_TARGETS_JSON)
    route_status = load_json(ROUTE_PROOF_STATUS_JSON)
    summary = manifest["summary"]
    priority_rows = [
        row for row in reference["focused_capture_plan"]
        if row.get("proof_status") == "needs_manual_capture"
    ][:7]
    return {
        "source": {
            "manifest": rel(MANIFEST_JSON),
            "reference_capture_plan": rel(REFERENCE_PLAN_JSON),
            "primary_visual_checklist": rel(PRIMARY_VISUAL_JSON),
            "v043_proof_status": rel(PROOF_STATUS_JSON),
            "route_fceux_targets": rel(ROUTE_TARGETS_JSON),
            "route_proof_status": rel(ROUTE_PROOF_STATUS_JSON),
        },
        "summary": {
            "primary_candidate": summary["primary_candidate"],
            "base_md5": summary["base_md5"],
            "primary_ips": summary["primary_ips"],
            "expected_patched_md5": summary["primary_candidate_md5"],
            "primary_visual_pending": primary_visual["summary"]["visual_pending_count"],
            "priority_manual_checks": len(priority_rows),
            "proof_status_counts": proof["summary"]["status_counts"],
            "route_status_counts": route_status["summary"]["status_counts"],
        },
        "primary_visual_rows": primary_visual["rows"],
        "route_watchers": route_targets["routes"],
        "priority_manual_checks": priority_rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    first_primary = payload["primary_visual_rows"][0] if payload["primary_visual_rows"] else {}
    first_primary_command = (
        f"python scripts/record_primary_visual_review.py {first_primary.get('rom_hit', '<rom_offset>')} "
        f"--confirm --screen-context \"{first_primary.get('screen_hint', 'visible matching screen context')} visible\""
    )
    lines = [
        "# Release Test Checklist",
        "",
        "Use this as the short path through the current manual-test bundle.",
        "",
        "## 1. Apply The Primary IPS",
        "",
        f"- Required base ROM MD5: `{summary['base_md5']}`",
        f"- Primary IPS: `{summary['primary_ips']}`",
        f"- Expected patched MD5: `{summary['expected_patched_md5']}`",
        "",
        "Repository command:",
        "",
        "```powershell",
        "python scripts/apply_primary_patch.py --output output/kunio_period_drama_korean_v0.4.2_test_applied.nes",
        "python scripts/verify_primary_patch.py",
        "```",
        "",
        "Bundle-only command:",
        "",
        "```powershell",
        "python apply_ips_standalone.py C:\\path\\to\\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes",
        "```",
        "",
        "## 2. Primary Screens To Check First",
        "",
        "Do not keep blind autoplay running on the title/first screen. First verify the rows already changed by the primary IPS.",
        "",
        f"- Pending primary visual checks: **{summary['primary_visual_pending']}**",
        "- Open patched ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`",
        "- Run watcher: `lua/kunio_manual_v042_capture_watch.lua`",
        "- Press `D` only on a visible matching text/menu/status screen.",
        "",
        "| # | ROM | romaji | human hint | Korean | evidence | screen hint |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(payload["primary_visual_rows"][:7], start=1):
        lines.append(
            f"| {index} | `{row['rom_hit']}` | {row['romaji']} | {row.get('meaning') or '-'} | "
            f"{row.get('korean_display') or '-'} | `{row['evidence_level']}` | {row['screen_hint']} |"
        )

    lines += [
        "",
        "After a matched primary screen:",
        "",
        "```powershell",
        first_primary_command,
        "python scripts/refresh_after_manual_capture.py --phase primary",
        "```",
        "",
        "## 3. Broad Screens For Future v0.4.3 Rows",
        "",
        "Use these only after primary visual review, or when you are already on the matching base-ROM route.",
        "",
        "| # | ROM | expected text | Korean | CPU guess | proof status | screen hint |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(payload["priority_manual_checks"], start=1):
        lines.append(
            f"| {index} | `{row['rom_offset']}` | {row['source_display']} | {row['korean_display']} | "
            f"`{row['cpu_address_guess']}` | `{row['proof_status']}` | {row['screen_hint']} |"
        )

    lines += [
        "",
        "## 4. Route Watchers",
        "",
        "Prefer these route wrappers over the all-target broad watcher. They show the active route and screen hint in the FCEUX overlay.",
        "",
        "| route | group | watcher | targets | screen hint |",
        "| ---: | --- | --- | ---: | --- |",
    ]
    for route in payload["route_watchers"]:
        first_target = route["targets"][0] if route["targets"] else {}
        lines.append(
            f"| {route['route']} | {route['group']} | `{route['watcher_lua']}` | "
            f"{route['target_count']} | {first_target.get('screen_hint', '')} |"
        )

    lines += [
        "",
        "Recommended next run:",
        "",
        "```text",
        "lua/kunio_manual_route_heishichi_capture_watch.lua",
        "```",
        "",
        "If the visible FCEUX screen is still the title/opening screen, stop with `Q`; do not wait.",
        "",
        "## 5. Capture Evidence",
        "",
        "For broad v0.4.3 candidates, open the base Japanese ROM, manually reach the target screen, then run:",
        "",
        "```text",
        "lua/kunio_manual_broad_scan_dump.lua",
        "```",
        "",
        "For several manually reached candidate screens in one session, run the matching route watcher once and press `D` on each target screen. Use the all-target watcher only if the route is unclear:",
        "",
        "```text",
        "lua/kunio_manual_broad_scan_capture_watch.lua",
        "```",
        "",
        "Then summarize and refresh the status reports:",
        "",
        "```powershell",
        "python scripts/analyze_broad_scan_manual_dump.py",
        "python scripts/generate_v043_proof_status.py",
        "python scripts/generate_manual_dump_inventory.py",
        "```",
        "",
        "## 6. Record v0.4.3 Visual Review",
        "",
        "Only after the visible screen matches the intended row:",
        "",
        "```powershell",
        "python scripts/record_visual_review.py 0x0440C --confirm --screen-context \"blacksmith label visible\"",
        "python scripts/build_v043_from_broad_scan_proof.py",
        "```",
        "",
        "## Rule",
        "",
        "- YouTube/transcription order helps choose screens, but does not approve ROM offsets.",
        "- v0.4.3 needs both CPU-read proof and explicit visual-context confirmation.",
        "- ROM files are local artifacts only and must not be distributed.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        "primary={primary_candidate} checks={priority_manual_checks}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

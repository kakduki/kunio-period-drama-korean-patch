#!/usr/bin/env python3
"""Run the core consistency checks for the Korean patch project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from rom_utils import REPO_ROOT


KEY_PYTHON = [
    "scripts/analyze_broad_scan_manual_dump.py",
    "scripts/analyze_manual_screen_dump.py",
    "scripts/apply_primary_patch.py",
    "scripts/apply_ips_standalone.py",
    "scripts/build_prg_patch_from_plan.py",
    "scripts/build_next_glyph_expansion_candidate.py",
    "scripts/build_broad_preview_candidate.py",
    "scripts/build_v041_conflict_safe_candidate.py",
    "scripts/build_v042_font_expanded_candidate.py",
    "scripts/build_v043_from_broad_scan_proof.py",
    "scripts/check_lua_target_syntax.py",
    "scripts/check_lua_script_balance.py",
    "scripts/compare_v04_broad_candidates.py",
    "scripts/generate_broad_scan_fceux_targets.py",
    "scripts/generate_broad_scan_patchability.py",
    "scripts/generate_batch46_text_readiness.py",
    "scripts/generate_manual_capture_cards.py",
    "scripts/generate_manual_capture_status.py",
    "scripts/generate_manual_dump_inventory.py",
    "scripts/generate_manual_proof_routes.py",
    "scripts/generate_next_glyph_expansion_plan.py",
    "scripts/generate_font_expansion_readiness.py",
    "scripts/generate_patch_candidate_manifest.py",
    "scripts/generate_patch_decision_matrix.py",
    "scripts/generate_primary_patch_contents.py",
    "scripts/generate_primary_visual_checklist.py",
    "scripts/generate_reference_capture_plan.py",
    "scripts/generate_release_test_checklist.py",
    "scripts/generate_route_fceux_targets.py",
    "scripts/generate_route_proof_status.py",
    "scripts/generate_translation_pattern_scan.py",
    "scripts/generate_translation_readable_reference.py",
    "scripts/generate_translation_glyph_coverage.py",
    "scripts/generate_translation_scan_capture_queue.py",
    "scripts/generate_v042_text_promotion_readiness.py",
    "scripts/generate_v042_manual_proof_packet.py",
    "scripts/generate_v043_proof_status.py",
    "scripts/generate_v041_fceux_targets.py",
    "scripts/generate_v04_fceux_targets.py",
    "scripts/package_primary_release.py",
    "scripts/record_visual_review.py",
    "scripts/readable_labels.py",
    "scripts/run_fceux_lua_analysis.py",
    "scripts/summarize_bank1_watch_reads.py",
    "scripts/test_analyze_manual_screen_dump.py",
    "scripts/test_broad_patchability_v042_bytes.py",
    "scripts/test_batch46_text_readiness.py",
    "scripts/test_font_expansion_readiness.py",
    "scripts/test_manual_dump_inventory.py",
    "scripts/test_manual_proof_routes.py",
    "scripts/test_primary_visual_checklist.py",
    "scripts/test_manual_capture_cards_readable.py",
    "scripts/test_run_fceux_budget.py",
    "scripts/test_reference_capture_plan.py",
    "scripts/test_release_test_checklist.py",
    "scripts/test_route_fceux_targets.py",
    "scripts/test_route_proof_status.py",
    "scripts/test_translation_capture_queue_readable.py",
    "scripts/test_v043_proof_gate.py",
    "scripts/test_v043_proof_status.py",
    "scripts/verify_broad_preview_patch.py",
    "scripts/verify_primary_patch.py",
]

LUA_TARGETS = [
    "lua/kunio_v041_conflict_safe_targets.lua",
    "lua/kunio_v04_equal_length_targets.lua",
    "lua/kunio_broad_scan_candidate_targets.lua",
    "lua/kunio_route_heishichi_targets.lua",
    "lua/kunio_route_kajiya_targets.lua",
    "lua/kunio_route_tatsuji_targets.lua",
    "lua/kunio_padding_exp_pad_00_targets.lua",
    "lua/kunio_padding_exp_pad_7a_targets.lua",
    "lua/kunio_padding_exp_pad_ff_targets.lua",
    "lua/kunio_padding_exp_pad_f8f9_targets.lua",
    "lua/kunio_padding_exp_preserve_tail_targets.lua",
]

LUA_SCRIPTS = [
    "lua/kunio_auto_dump.lua",
    "lua/kunio_autoplay_watch.lua",
    "lua/kunio_bank1_watch.lua",
    "lua/kunio_manual_broad_scan_dump.lua",
    "lua/kunio_manual_broad_scan_capture_watch.lua",
    "lua/kunio_manual_capture_watch.lua",
    "lua/kunio_manual_route_heishichi_capture_watch.lua",
    "lua/kunio_manual_route_kajiya_capture_watch.lua",
    "lua/kunio_manual_route_tatsuji_capture_watch.lua",
    "lua/kunio_manual_screen_dump.lua",
    "lua/kunio_manual_v042_capture_watch.lua",
    "lua/kunio_manual_v04_screen_dump.lua",
    "lua/kunio_manual_v041_screen_dump.lua",
    "lua/kunio_manual_v042_screen_dump.lua",
    "lua/kunio_ppu_watch.lua",
]

REGEN_COMMANDS = [
    ["scripts/compare_v04_broad_candidates.py"],
    ["scripts/build_v041_conflict_safe_candidate.py"],
    ["scripts/generate_v041_fceux_targets.py"],
    ["scripts/generate_translation_readable_reference.py"],
    ["scripts/generate_translation_pattern_scan.py"],
    ["scripts/generate_translation_scan_capture_queue.py"],
    ["scripts/generate_translation_glyph_coverage.py"],
    ["scripts/generate_next_glyph_expansion_plan.py"],
    ["scripts/generate_font_expansion_readiness.py"],
    ["scripts/generate_broad_scan_patchability.py"],
    ["scripts/generate_broad_scan_fceux_targets.py"],
    ["scripts/build_next_glyph_expansion_candidate.py", "--batch-size", "32"],
    ["scripts/build_next_glyph_expansion_candidate.py", "--batch-size", "46"],
    ["scripts/generate_batch46_text_readiness.py"],
    ["scripts/build_v042_font_expanded_candidate.py"],
    ["scripts/build_broad_preview_candidate.py"],
    ["scripts/generate_patch_candidate_manifest.py"],
    ["scripts/generate_patch_decision_matrix.py"],
    ["scripts/generate_primary_patch_contents.py"],
    ["scripts/generate_primary_visual_checklist.py"],
    ["scripts/generate_v042_text_promotion_readiness.py"],
    ["scripts/generate_v042_manual_proof_packet.py"],
    ["scripts/generate_manual_proof_routes.py"],
    ["scripts/generate_route_fceux_targets.py"],
    ["scripts/generate_route_proof_status.py"],
    ["scripts/analyze_broad_scan_manual_dump.py"],
    ["scripts/build_v043_from_broad_scan_proof.py"],
    ["scripts/generate_v043_proof_status.py"],
    ["scripts/generate_reference_capture_plan.py"],
    ["scripts/generate_release_test_checklist.py"],
    ["scripts/generate_manual_capture_cards.py"],
    ["scripts/generate_manual_capture_status.py"],
    ["scripts/generate_manual_dump_inventory.py"],
]


def run(label: str, args: list[str]) -> None:
    command = [sys.executable, *args]
    print(f"\n== {label} ==")
    print(" ".join(command))
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)


def check_manifest() -> None:
    manifest = json.loads((REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json").read_text(encoding="utf-8"))
    summary = manifest["summary"]
    expected = {
        "primary_candidate": "v0.4.2 font-expanded",
        "primary_candidate_md5": "ea11dc002a1a7b07682ce00a754b1a61",
        "primary_ips_apply_matches_rom": True,
        "v04_broad_conflict_count": 3,
        "v04_broad_high_conflict_count": 3,
    }
    errors = []
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"{key}: expected {value!r}, got {summary.get(key)!r}")
    if errors:
        print("\n== manifest invariants ==")
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("\n== manifest invariants ==")
    print("OK: primary candidate, IPS verification, and conflict counts match expectations.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regen",
        action="store_true",
        help="Regenerate conflict reports, v0.4.1 candidate, v0.4.1 targets, and manifest before checking.",
    )
    args = parser.parse_args()

    run("python compile", ["-m", "py_compile", *KEY_PYTHON])
    if args.regen:
        for command in REGEN_COMMANDS:
            run("regenerate " + command[0], command)
    run("lua script balance", ["scripts/check_lua_script_balance.py", *LUA_SCRIPTS])
    run("lua target syntax", ["scripts/check_lua_target_syntax.py", *LUA_TARGETS])
    run("FCEUX autoplay budget guard", ["scripts/test_run_fceux_budget.py"])
    run("manual dump inventory", ["scripts/test_manual_dump_inventory.py"])
    run("manual screen dump analyzer", ["scripts/test_analyze_manual_screen_dump.py"])
    run("font expansion readiness", ["scripts/test_font_expansion_readiness.py"])
    run("manual proof routes", ["scripts/test_manual_proof_routes.py"])
    run("primary visual checklist", ["scripts/test_primary_visual_checklist.py"])
    run("manual capture cards readable labels", ["scripts/test_manual_capture_cards_readable.py"])
    run("reference-guided capture plan", ["scripts/test_reference_capture_plan.py"])
    run("release test checklist", ["scripts/test_release_test_checklist.py"])
    run("route FCEUX targets", ["scripts/test_route_fceux_targets.py"])
    run("route proof status", ["scripts/test_route_proof_status.py"])
    run("translation capture queue readable labels", ["scripts/test_translation_capture_queue_readable.py"])
    run("broad patchability v0.4.2 planned bytes", ["scripts/test_broad_patchability_v042_bytes.py"])
    run("batch46 text readiness", ["scripts/test_batch46_text_readiness.py"])
    run("v0.4.3 proof gate", ["scripts/test_v043_proof_gate.py"])
    run("v0.4.3 proof status", ["scripts/test_v043_proof_status.py"])
    run("primary IPS verification", ["scripts/verify_primary_patch.py"])
    run("broad preview IPS verification", ["scripts/verify_broad_preview_patch.py"])
    check_manifest()
    print("\nAll project checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
    "scripts/analyze_reference_ips.py",
    "scripts/analyze_full_script_font_capacity.py",
    "scripts/analyze_dialogue_renderer.py",
    "scripts/analyze_english_font_slots.py",
    "scripts/analyze_main_menu_context.py",
    "scripts/analyze_main_menu_items_context.py",
    "scripts/analyze_main_menu_korean_candidate.py",
    "scripts/build_main_menu_korean_candidate.py",
    "scripts/generate_main_menu_pipeline_artifacts.py",
    "scripts/analyze_opening_dialogue_proof_capture.py",
    "scripts/analyze_opening_dialogue_renderer_probe.py",
    "scripts/analyze_opening_mapper_trace.py",
    "scripts/audit_korean_square_font.py",
    "scripts/korean_font_quality.py",
    "scripts/generate_readability_proof_artifacts.py",
    "scripts/audit_opening_font_runtime_mapping.py",
    "scripts/compile_korean_scene_batch.py",
    "scripts/build_pointer_dialogue_catalog.py",
    "scripts/extract_english_reference_script.py",
    "scripts/analyze_broad_scan_manual_dump.py",
    "scripts/analyze_manual_screen_dump.py",
    "scripts/apply_primary_patch.py",
    "scripts/apply_ips_standalone.py",
    "scripts/audit_candidate_patch_scope.py",
    "scripts/audit_padding_experiment_pipeline.py",
    "scripts/build_prg_patch_from_plan.py",
    "scripts/build_next_glyph_expansion_candidate.py",
    "scripts/build_broad_preview_candidate.py",
    "scripts/build_candidate_pipeline.py",
    "scripts/build_opening_dialogue_proof.py",
    "scripts/build_opening_dialogue_8x16_proof.py",
    "scripts/build_opening_dialogue_16x16_proof.py",
    "scripts/build_opening_dialogue_16x16_capacity.py",
    "scripts/build_opening_dialogue_182_183_16x16.py",
    "scripts/build_pointer_dialogue_batch_candidate.py",
    "scripts/build_pointer_dialogue_8x16_candidate.py",
    "scripts/analyze_pointer_dialogue_korean_draft.py",
    "scripts/audit_full_pointer_korean_layout.py",
    "scripts/audit_full_pointer_translation.py",
    "scripts/analyze_full_pointer_forced_samples.py",
    "scripts/plan_pointer_font_pages.py",
    "scripts/pointer_page_loader.py",
    "scripts/update_pointer_dialogue_8x16_runtime_report.py",
    "scripts/build_opening_dialogue_bank8_page_switch_proof.py",
    "scripts/build_opening_dialogue_bank8_persistent_page_proof.py",
    "scripts/build_opening_dialogue_bank8_static_r1_page_proof.py",
    "scripts/build_opening_dialogue_bank8_static_r1_capacity_tier2.py",
    "scripts/build_opening_dialogue_bank8_static_r1_safe_capacity_tier2.py",
    "scripts/build_v041_conflict_safe_candidate.py",
    "scripts/build_v042_font_expanded_candidate.py",
    "scripts/build_v043_from_broad_scan_proof.py",
    "scripts/build_ptr181_bank8_page_probe.py",
    "scripts/build_ptr181_dynamic_page_probe.py",
    "scripts/build_ptr181_conditional_mapper_probe.py",
    "scripts/build_ptr181_expanded_chr_probe.py",
    "scripts/build_ptr181_expanded_code_pool_probe.py",
    "scripts/build_ptr181_korean_8x16_candidate.py",
    "scripts/build_ptr181_pointer_page_candidate.py",
    "scripts/build_full_pointer_korean_candidate.py",
    "tools/insert_text.py",
    "tools/realtime_translation_overlay.py",
    "scripts/check_lua_target_syntax.py",
    "scripts/check_lua_script_balance.py",
    "scripts/confirm_next_primary_visual.py",
    "scripts/compare_v04_broad_candidates.py",
    "scripts/convert_fceux_gd_to_png.py",
    "scripts/generate_broad_scan_fceux_targets.py",
    "scripts/generate_broad_scan_patchability.py",
    "scripts/generate_batch46_text_readiness.py",
    "scripts/generate_auto_input_evidence_report.py",
    "scripts/generate_auto_input_review_crops.py",
    "scripts/generate_auto_input_visual_triage.py",
    "scripts/generate_current_primary_visual_task.py",
    "scripts/generate_katana_visual_explorer_report.py",
    "scripts/generate_katana_inventory_slot_candidates.py",
    "scripts/generate_manual_capture_cards.py",
    "scripts/generate_manual_capture_status.py",
    "scripts/generate_manual_dump_inventory.py",
    "scripts/generate_manual_proof_routes.py",
    "scripts/generate_next_glyph_expansion_plan.py",
    "scripts/generate_next_manual_run.py",
    "scripts/generate_object_state_probe_candidates.py",
    "scripts/generate_boss_dialogue_targets.py",
    "scripts/summarize_boss_forced_render.py",
    "scripts/generate_object_state_pair_plan.py",
    "scripts/generate_font_expansion_readiness.py",
    "scripts/generate_patch_candidate_manifest.py",
    "scripts/generate_patch_decision_matrix.py",
    "scripts/generate_patch_progress_dashboard.py",
    "scripts/generate_padding_strategy_priority.py",
    "scripts/generate_primary_patch_contents.py",
    "scripts/generate_primary_visual_checklist.py",
    "scripts/generate_reference_capture_plan.py",
    "scripts/generate_release_test_checklist.py",
    "scripts/generate_release_gate_action_plan.py",
    "scripts/generate_route_fceux_targets.py",
    "scripts/generate_route_proof_status.py",
    "scripts/generate_state_cheat_probe_candidates.py",
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
    "scripts/paired_dialogue_helper.py",
    "scripts/korean_tile_font.py",
    "scripts/prepare_next_manual_run.py",
    "scripts/preflight_manual_fceux.py",
    "scripts/preflight_release_gate_action.py",
    "scripts/record_primary_visual_review.py",
    "scripts/record_visual_review.py",
    "scripts/readable_labels.py",
    "scripts/refresh_after_manual_capture.py",
    "scripts/run_fceux_lua_analysis.py",
    "scripts/run_next_manual_fceux.py",
    "scripts/summarize_bank1_watch_reads.py",
    "scripts/test_analyze_manual_screen_dump.py",
    "scripts/test_analyze_dialogue_renderer.py",
    "scripts/test_analyze_english_font_slots.py",
    "scripts/test_analyze_main_menu_context.py",
    "scripts/test_analyze_main_menu_items_context.py",
    "scripts/test_analyze_main_menu_korean_candidate.py",
    "scripts/analyze_korean_development_candidate.py",
    "scripts/analyze_pointer_dialogue_batch_probe.py",
    "scripts/build_korean_development_candidate.py",
    "scripts/test_build_main_menu_korean_candidate.py",
    "scripts/test_build_korean_development_candidate.py",
    "scripts/test_default_build_reproducibility.py",
    "scripts/test_external_output_paths.py",
    "scripts/test_analyze_pointer_dialogue_batch_probe.py",
    "scripts/test_generate_main_menu_pipeline_artifacts.py",
    "scripts/test_analyze_opening_dialogue_proof_capture.py",
    "scripts/test_analyze_opening_dialogue_renderer_probe.py",
    "scripts/test_analyze_opening_mapper_trace.py",
    "scripts/test_audit_korean_square_font.py",
    "scripts/test_korean_font_quality.py",
    "scripts/test_generate_readability_proof_artifacts.py",
    "scripts/test_audit_opening_font_runtime_mapping.py",
    "scripts/test_compile_korean_scene_batch.py",
    "scripts/test_build_pointer_dialogue_catalog.py",
    "scripts/test_analyze_reference_ips.py",
    "scripts/test_analyze_full_script_font_capacity.py",
    "scripts/test_extract_english_reference_script.py",
    "scripts/test_auto_input_evidence_report.py",
    "scripts/test_auto_input_review_crops.py",
    "scripts/test_auto_input_visual_triage.py",
    "scripts/test_current_primary_visual_task.py",
    "scripts/test_katana_visual_explorer_report.py",
    "scripts/test_katana_inventory_slot_candidates.py",
    "scripts/test_kunio_sram_route_probe.py",
    "scripts/test_kunio_name_entry_probe.py",
    "scripts/test_broad_patchability_v042_bytes.py",
    "scripts/test_batch46_text_readiness.py",
    "scripts/test_build_opening_dialogue_proof.py",
    "scripts/test_build_opening_dialogue_8x16_proof.py",
    "scripts/test_build_opening_dialogue_16x16_proof.py",
    "scripts/test_build_opening_dialogue_16x16_capacity.py",
    "scripts/test_build_opening_dialogue_182_183_16x16.py",
    "scripts/test_build_pointer_dialogue_batch_candidate.py",
    "scripts/test_build_pointer_dialogue_8x16_candidate.py",
    "scripts/test_analyze_pointer_dialogue_korean_draft.py",
    "scripts/test_audit_full_pointer_korean_layout.py",
    "scripts/test_audit_full_pointer_translation.py",
    "scripts/test_analyze_full_pointer_forced_samples.py",
    "scripts/test_plan_pointer_font_pages.py",
    "scripts/test_pointer_page_loader.py",
    "scripts/test_build_opening_dialogue_182_184_16x16.py",
    "scripts/test_build_opening_dialogue_bank8_page_switch_proof.py",
    "scripts/test_build_opening_dialogue_bank8_persistent_page_proof.py",
    "scripts/test_build_opening_dialogue_bank8_static_r1_page_proof.py",
    "scripts/test_build_opening_dialogue_bank8_static_r1_capacity_tier2.py",
    "scripts/test_build_opening_dialogue_bank8_static_r1_safe_capacity_tier2.py",
    "scripts/test_candidate_pipeline_reports.py",
    "scripts/test_candidate_ips_apply.py",
    "scripts/test_ips_extension.py",
    "scripts/test_candidate_patch_scope.py",
    "scripts/test_confirm_next_primary_visual.py",
    "scripts/test_convert_fceux_gd_to_png.py",
    "scripts/test_font_expansion_readiness.py",
    "scripts/test_manual_dump_inventory.py",
    "scripts/test_manual_proof_routes.py",
    "scripts/test_manual_capture_watcher_overlay.py",
    "scripts/test_next_manual_run.py",
    "scripts/test_object_state_probe_candidates.py",
    "scripts/test_generate_boss_dialogue_targets.py",
    "scripts/test_summarize_boss_forced_render.py",
    "scripts/test_object_state_pair_plan.py",
    "scripts/test_patch_progress_dashboard.py",
    "scripts/test_padding_strategy_priority.py",
    "scripts/test_patch_progress_dashboard_discoverability.py",
    "scripts/test_prepare_next_manual_run.py",
    "scripts/test_preflight_manual_fceux.py",
    "scripts/test_preflight_release_gate_action.py",
    "scripts/test_preflight_release_gate_action_bundle.py",
    "scripts/test_paired_dialogue_helper.py",
    "scripts/test_primary_visual_checklist.py",
    "scripts/test_record_primary_visual_review.py",
    "scripts/test_manual_capture_cards_readable.py",
    "scripts/test_korean_tile_font.py",
    "scripts/test_run_fceux_budget.py",
    "scripts/test_run_next_manual_fceux.py",
    "scripts/test_reference_capture_plan.py",
    "scripts/test_refresh_after_manual_capture.py",
    "scripts/test_release_package_contents.py",
    "scripts/test_release_gate_action_plan.py",
    "scripts/test_release_test_checklist.py",
    "scripts/test_route_fceux_targets.py",
    "scripts/test_route_proof_status.py",
    "scripts/test_state_cheat_probe_candidates.py",
    "scripts/test_state_single_byte_probe_lua.py",
    "scripts/test_translation_capture_queue_readable.py",
    "scripts/test_v043_proof_gate.py",
    "scripts/test_v042_manual_proof_packet.py",
    "scripts/test_v043_proof_status.py",
    "scripts/test_build_ptr181_bank8_page_probe.py",
    "scripts/test_build_ptr181_dynamic_page_probe.py",
    "scripts/test_build_ptr181_conditional_mapper_probe.py",
    "scripts/test_build_ptr181_expanded_chr_probe.py",
    "scripts/test_build_ptr181_expanded_code_pool_probe.py",
    "scripts/test_build_ptr181_korean_8x16_candidate.py",
    "scripts/test_build_ptr181_pointer_page_candidate.py",
    "scripts/test_build_full_pointer_korean_candidate.py",
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
    "lua/kunio_opening_dialogue_proof_target.lua",
    "lua/kunio_opening_dialogue_16x16_proof_target.lua",
    "lua/kunio_opening_dialogue_16x16_capacity_tier1_target.lua",
    "lua/kunio_opening_dialogue_16x16_capacity_tier2_target.lua",
    "lua/kunio_opening_dialogue_16x16_relocation_proof_target.lua",
    "lua/kunio_opening_dialogue_16x16_speaker_separator_proof_target.lua",
    "lua/kunio_opening_dialogue_16x16_readability_proof_target.lua",
    "lua/kunio_opening_ptr_183_base_target.lua",
    "lua/kunio_opening_ptr_184_base_target.lua",
    "lua/kunio_opening_ptr_182_183_16x16_p182_target.lua",
    "lua/kunio_opening_ptr_182_183_16x16_p183_target.lua",
    "lua/kunio_opening_ptr_182_184_16x16_p182_target.lua",
    "lua/kunio_opening_ptr_182_184_16x16_p183_target.lua",
    "lua/kunio_opening_ptr_182_184_16x16_p184_target.lua",
    "lua/kunio_pointer_dialogue_batch_002_003_target.lua",
    "lua/kunio_opening_dialogue_bank8_page_switch_proof_target.lua",
    "lua/kunio_opening_dialogue_bank8_persistent_page_proof_target.lua",
    "lua/kunio_opening_ptr_185_base_target.lua",
    "lua/kunio_translation_overlay_targets.lua",
]

LUA_SCRIPTS = [
    "lua/kunio_auto_dump.lua",
    "lua/kunio_opening_dialogue_proof.lua",
    "lua/kunio_opening_ptr_183_probe.lua",
    "lua/kunio_opening_ptr_184_base_probe.lua",
    "lua/kunio_main_menu_context_probe.lua",
    "lua/kunio_opening_mapper_trace.lua",
    "lua/kunio_opening_dialogue_renderer_probe.lua",
    "lua/kunio_autoplay_watch.lua",
    "lua/kunio_bank1_watch.lua",
    "lua/kunio_input_explorer_v042.lua",
    "lua/kunio_katana_inventory_probe_v042.lua",
    "lua/kunio_katana_autoplay_route_capture_v042.lua",
    "lua/kunio_katana_itemlist_state_probe_v042.lua",
    "lua/kunio_katana_single_slot_probe_v042.lua",
    "lua/kunio_katana_visual_explorer_v042.lua",
    "lua/kunio_state_single_byte_probe.lua",
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
    "lua/kunio_pointer_dialogue_batch_probe.lua",
    "lua/kunio_pointer_dialogue_route_probe.lua",
    "lua/kunio_pointer_dialogue_batch_000_002_8x16_probe.lua",
    "lua/kunio_ptr181_renderer_probe.lua",
    "lua/kunio_ptr181_pointer_loader_probe.lua",
    "lua/kunio_ptr181_page_restore_probe.lua",
    "lua/kunio_stage_progression_probe.lua",
    "lua/kunio_full_pointer_dialogue_input_probe.lua",
    "lua/kunio_sram_route_probe.lua",
    "lua/kunio_name_entry_probe.lua",
    "lua/kunio_translation_overlay.lua",
    "lua/kunio_opening_ptr_185_base_probe.lua",
    "lua/kunio_map_crsr_source_probe.lua",
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
    ["scripts/generate_next_manual_run.py"],
    ["scripts/generate_current_primary_visual_task.py"],
    ["scripts/build_candidate_pipeline.py"],
    ["scripts/audit_candidate_patch_scope.py"],
    ["scripts/generate_padding_strategy_priority.py"],
    ["scripts/generate_release_gate_action_plan.py"],
    ["scripts/generate_patch_progress_dashboard.py"],
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
    run("next manual FCEUX launcher", ["scripts/test_run_next_manual_fceux.py"])
    run("confirm next primary visual", ["scripts/test_confirm_next_primary_visual.py"])
    run("FCEUX GD screenshot converter", ["scripts/test_convert_fceux_gd_to_png.py"])
    run("manual dump inventory", ["scripts/test_manual_dump_inventory.py"])
    run("manual screen dump analyzer", ["scripts/test_analyze_manual_screen_dump.py"])
    run("dialogue renderer analyzer", ["scripts/test_analyze_dialogue_renderer.py"])
    run("English reference font slot mapper", ["scripts/test_analyze_english_font_slots.py"])
    run("main-menu context analyzer", ["scripts/test_analyze_main_menu_context.py"])
    run("main-menu Items context analyzer", ["scripts/test_analyze_main_menu_items_context.py"])
    run("main-menu Korean candidate smoke analyzer", ["scripts/test_analyze_main_menu_korean_candidate.py"])
    run("main-menu Korean 16x16 candidate", ["scripts/test_build_main_menu_korean_candidate.py"])
    run("combined Korean development candidate", ["scripts/test_build_korean_development_candidate.py"])
    run("default build reproducibility", ["scripts/test_default_build_reproducibility.py"])
    run("selected-only manifest plan", ["scripts/test_insert_text_manifest.py"])
    run("realtime translation overlay receiver", ["scripts/test_realtime_translation_overlay.py"])
    run("external output paths", ["scripts/test_external_output_paths.py"])
    run("main-menu pipeline artifact generator", ["scripts/test_generate_main_menu_pipeline_artifacts.py"])
    run("opening dialogue proof capture analyzer", ["scripts/test_analyze_opening_dialogue_proof_capture.py"])
    run("opening dialogue renderer probe analyzer", ["scripts/test_analyze_opening_dialogue_renderer_probe.py"])
    run("opening MMC3 mapper trace analyzer", ["scripts/test_analyze_opening_mapper_trace.py"])
    run("Korean 16x16 font comparison", ["scripts/test_audit_korean_square_font.py"])
    run("Korean 16x16 font-quality gate", ["scripts/test_korean_font_quality.py"])
    run("readability proof pipeline artifacts", ["scripts/test_generate_readability_proof_artifacts.py"])
    run("opening font runtime mapping audit", ["scripts/test_audit_opening_font_runtime_mapping.py"])
    run("Korean scene-batch compiler", ["scripts/test_compile_korean_scene_batch.py"])
    run("complete pointer dialogue catalog", ["scripts/test_build_pointer_dialogue_catalog.py"])
    run("opening dialogue proof patch", ["scripts/test_build_opening_dialogue_proof.py"])
    run("opening dialogue 8x16 proof patch", ["scripts/test_build_opening_dialogue_8x16_proof.py"])
    run("opening dialogue paired 16x16 proof patch", ["scripts/test_build_opening_dialogue_16x16_proof.py"])
    run("opening dialogue catalog-driven paired 16x16 capacity", ["scripts/test_build_opening_dialogue_16x16_capacity.py"])
    run("two-record opening Korean 16x16 candidate", ["scripts/test_build_opening_dialogue_182_183_16x16.py"])
    run("three-record range-scoped opening Korean 16x16 candidate", ["scripts/test_build_opening_dialogue_182_184_16x16.py"])
    run("multi-record pointer dialogue Korean candidate", ["scripts/test_build_pointer_dialogue_batch_candidate.py"])
    run("pointer dialogue bounded runtime analyzer", ["scripts/test_analyze_pointer_dialogue_batch_probe.py"])
    run("full pointer translation audit", ["scripts/test_audit_full_pointer_translation.py"])
    run("full pointer forced page samples", ["scripts/test_analyze_full_pointer_forced_samples.py"])
    run("opening dialogue Bank 8 page-switch proof", ["scripts/test_build_opening_dialogue_bank8_page_switch_proof.py"])
    run("opening dialogue Bank 8 persistent page proof", ["scripts/test_build_opening_dialogue_bank8_persistent_page_proof.py"])
    run("Korean tile font serialization", ["scripts/test_korean_tile_font.py"])
    run("record-scoped paired dialogue helper", ["scripts/test_paired_dialogue_helper.py"])
    run("reference IPS analyzer", ["scripts/test_analyze_reference_ips.py"])
    run(
        "English reference script extractor",
        ["scripts/test_extract_english_reference_script.py"],
    )
    run("boss dialogue targets", ["scripts/test_generate_boss_dialogue_targets.py"])
    run("boss dialogue forced renderer report", ["scripts/test_summarize_boss_forced_render.py"])

    run("auto-input evidence report", ["scripts/test_auto_input_evidence_report.py"])
    run("auto-input review crops", ["scripts/test_auto_input_review_crops.py"])
    run("auto-input visual triage", ["scripts/test_auto_input_visual_triage.py"])
    run("current primary visual task", ["scripts/test_current_primary_visual_task.py"])
    run("Katana visual explorer report", ["scripts/test_katana_visual_explorer_report.py"])
    run("Katana inventory slot candidates", ["scripts/test_katana_inventory_slot_candidates.py"])
    run("SRAM route probe", ["scripts/test_kunio_sram_route_probe.py"])
    run("Koganemushi name-entry probe", ["scripts/test_kunio_name_entry_probe.py"])
    run("font expansion readiness", ["scripts/test_font_expansion_readiness.py"])
    run("manual proof routes", ["scripts/test_manual_proof_routes.py"])
    run("manual capture watcher overlay", ["scripts/test_manual_capture_watcher_overlay.py"])
    run("next manual run", ["scripts/test_next_manual_run.py"])
    run("patch progress dashboard", ["scripts/test_patch_progress_dashboard.py"])
    run("patch progress dashboard discoverability", ["scripts/test_patch_progress_dashboard_discoverability.py"])
    run("next manual run helper", ["scripts/test_prepare_next_manual_run.py"])
    run("manual FCEUX preflight", ["scripts/test_preflight_manual_fceux.py"])
    run("release gate action preflight", ["scripts/test_preflight_release_gate_action.py"])
    run("release gate action preflight bundle", ["scripts/test_preflight_release_gate_action_bundle.py"])
    run("primary visual checklist", ["scripts/test_primary_visual_checklist.py"])
    run("primary visual review recorder", ["scripts/test_record_primary_visual_review.py"])
    run("manual capture cards readable labels", ["scripts/test_manual_capture_cards_readable.py"])
    run("reference-guided capture plan", ["scripts/test_reference_capture_plan.py"])
    run("manual capture refresh helper", ["scripts/test_refresh_after_manual_capture.py"])
    run("release package contents", ["scripts/test_release_package_contents.py"])
    run("release gate action plan", ["scripts/test_release_gate_action_plan.py"])
    run("release test checklist", ["scripts/test_release_test_checklist.py"])
    run("route FCEUX targets", ["scripts/test_route_fceux_targets.py"])
    run("route proof status", ["scripts/test_route_proof_status.py"])
    run("translation capture queue readable labels", ["scripts/test_translation_capture_queue_readable.py"])
    run("broad patchability v0.4.2 planned bytes", ["scripts/test_broad_patchability_v042_bytes.py"])
    run("candidate pipeline reports", ["scripts/test_candidate_pipeline_reports.py"])
    run("candidate IPS apply", ["scripts/test_candidate_ips_apply.py"])
    run("candidate patch scope audit", ["scripts/test_candidate_patch_scope.py"])
    run("padding strategy priority", ["scripts/test_padding_strategy_priority.py"])
    run("batch46 text readiness", ["scripts/test_batch46_text_readiness.py"])
    run("v0.4.3 proof gate", ["scripts/test_v043_proof_gate.py"])
    run("v0.4.2 manual proof packet", ["scripts/test_v042_manual_proof_packet.py"])
    run("v0.4.3 proof status", ["scripts/test_v043_proof_status.py"])
    run("primary IPS verification", ["scripts/verify_primary_patch.py"])
    run("broad preview IPS verification", ["scripts/verify_broad_preview_patch.py"])
    check_manifest()
    print("\nAll project checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

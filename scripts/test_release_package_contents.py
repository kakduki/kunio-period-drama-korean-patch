#!/usr/bin/env python3
"""Check the ROM-free release test bundle includes soft-gate pipeline evidence."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from rom_utils import REPO_ROOT


CANDIDATE_PIPELINE_DIR = REPO_ROOT / "rom_analysis" / "candidate_pipeline"
BUNDLE_DIR = REPO_ROOT / "release" / "kunio_period_drama_korean_v0_4_2_font-expanded_test"
ZIP_PATH = BUNDLE_DIR.with_suffix(".zip")


def main() -> int:
    errors: list[str] = []
    if not BUNDLE_DIR.is_dir():
        errors.append(f"release bundle missing: {BUNDLE_DIR.relative_to(REPO_ROOT)}")
    if not ZIP_PATH.is_file():
        errors.append(f"release zip missing: {ZIP_PATH.relative_to(REPO_ROOT)}")
    if not CANDIDATE_PIPELINE_DIR.is_dir():
        errors.append(f"candidate pipeline dir missing: {CANDIDATE_PIPELINE_DIR.relative_to(REPO_ROOT)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    source_files = sorted(path for path in CANDIDATE_PIPELINE_DIR.rglob("*") if path.is_file())
    if not source_files:
        errors.append("candidate pipeline source has no files")

    required_names = {
        "build_matrix.md",
        "string_candidates.csv",
        "false_positive_list.csv",
        "patched_rom_report.md",
        "smoke_test_log.txt",
        "release_gate_checklist.md",
        "release_gate_checklist.json",
        "release_gate_action_plan.md",
        "release_gate_action_plan.json",
        "high_risk_candidates.csv",
        "padding_experiment_matrix.md",
        "padding_experiment_matrix.json",
        "padding_experiment_matrix.csv",
    }
    source_names = {path.name for path in source_files}
    for name in sorted(required_names - source_names):
        errors.append(f"candidate pipeline source missing required artifact: {name}")

    for path in BUNDLE_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() == ".nes":
            errors.append(f"release bundle contains ROM file: {path.relative_to(REPO_ROOT)}")

    readme = BUNDLE_DIR / "README.md"
    readme_text = readme.read_text(encoding="utf-8")
    if "candidate_pipeline/" not in readme_text:
        errors.append("release README does not mention candidate_pipeline/")
    if "candidate_pipeline/release_gate_action_plan.md" not in readme_text:
        errors.append("release README does not mention candidate_pipeline/release_gate_action_plan.md")
    if "preflight_release_gate_action.py" not in readme_text:
        errors.append("release README does not mention preflight_release_gate_action.py")
    if not (BUNDLE_DIR / "preflight_release_gate_action.py").is_file():
        errors.append("release bundle missing preflight_release_gate_action.py")
    for required_bundle_file in [
        "audit_padding_experiment_pipeline.py",
        "generate_patch_progress_dashboard.py",
        "katana_single_slot_probe_0508_notes.md",
        "katana_single_slot_probe_0509_notes.md",
        "katana_runtime_state_probe_0700_itemlist_notes.md",
        "katana_itemlist_state_probe_v042_early_notes.md",
        "lua/kunio_katana_itemlist_state_probe_v042.lua",
        "lua/kunio_auto_dump.lua",
    ]:
        if not (BUNDLE_DIR / required_bundle_file).is_file():
            errors.append(f"release bundle missing {required_bundle_file}")

    manifest_path = BUNDLE_DIR / "release_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_files = set(manifest.get("files", []))

    with zipfile.ZipFile(ZIP_PATH) as archive:
        zip_names = set(archive.namelist())
        zip_roms = [name for name in zip_names if name.lower().endswith(".nes")]
        if zip_roms:
            errors.append(f"release zip contains ROM files: {zip_roms}")

        for source in source_files:
            relative = source.relative_to(CANDIDATE_PIPELINE_DIR).as_posix()
            bundle_relative = f"candidate_pipeline/{relative}"
            repo_relative = (BUNDLE_DIR / bundle_relative).relative_to(REPO_ROOT).as_posix()
            zip_relative = f"{BUNDLE_DIR.name}/{bundle_relative}"
            if not (BUNDLE_DIR / bundle_relative).is_file():
                errors.append(f"bundle missing candidate pipeline file: {bundle_relative}")
            if repo_relative not in manifest_files:
                errors.append(f"manifest missing candidate pipeline file: {repo_relative}")
            if zip_relative not in zip_names:
                errors.append(f"zip missing candidate pipeline file: {zip_relative}")
        if f"{BUNDLE_DIR.name}/preflight_release_gate_action.py" not in zip_names:
            errors.append("zip missing preflight_release_gate_action.py")
        for required_bundle_file in [
            "audit_padding_experiment_pipeline.py",
            "generate_patch_progress_dashboard.py",
            "katana_single_slot_probe_0508_notes.md",
            "katana_single_slot_probe_0509_notes.md",
            "katana_runtime_state_probe_0700_itemlist_notes.md",
            "katana_itemlist_state_probe_v042_early_notes.md",
            "lua/kunio_katana_itemlist_state_probe_v042.lua",
            "lua/kunio_auto_dump.lua",
        ]:
            if f"{BUNDLE_DIR.name}/{required_bundle_file}" not in zip_names:
                errors.append(f"zip missing {required_bundle_file}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: release package includes {len(source_files)} candidate pipeline files and no ROM files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

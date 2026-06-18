#!/usr/bin/env python3
"""Check whether the next manual FCEUX capture is ready to run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from run_fceux_lua_analysis import find_fceux
from rom_utils import REPO_ROOT


NEXT_MANUAL_RUN = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
CURRENT_PRIMARY_VISUAL_TASK = REPO_ROOT / "rom_analysis" / "current_primary_visual_task.json"
MANIFEST = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"
DEFAULT_MANUAL_TIMEOUT = 600
DEFAULT_MANUAL_OUTPUT = "rom_analysis/fceux_manual_launch"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(raw: object) -> Path:
    path = Path(str(raw))
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def load_next_manual_context() -> dict[str, object]:
    manifest = load_json(MANIFEST)
    next_run = load_json(NEXT_MANUAL_RUN)
    action = next_run.get("next_action")
    current_visual_task = load_json(CURRENT_PRIMARY_VISUAL_TASK) if CURRENT_PRIMARY_VISUAL_TASK.exists() else {}
    return {
        "manifest": manifest,
        "next_run": next_run,
        "action": action,
        "current_visual_task": current_visual_task,
    }


def launch_command(action: dict[str, object], *, timeout: int = DEFAULT_MANUAL_TIMEOUT) -> list[str]:
    target_rom = resolve_repo_path(action["rom_to_open"])
    watcher = resolve_repo_path(action["watcher_lua"])
    return [
        "scripts/run_fceux_lua_analysis.py",
        "--rom",
        rel(target_rom),
        "--lua-script",
        rel(watcher),
        "--timeout",
        str(timeout),
        "--stop-after-manual-dump",
        "--final-output",
        DEFAULT_MANUAL_OUTPUT,
        "--clean-output",
        "--no-dump-hex",
        "--no-dump-bin",
    ]


def validate_next_action(context: dict[str, object]) -> tuple[list[str], list[str]]:
    manifest = context["manifest"]
    action = context["action"]
    current_visual_task = context.get("current_visual_task", {})
    if not isinstance(manifest, dict) or not isinstance(action, dict):
        return [], []

    summary = manifest["summary"]
    errors: list[str] = []
    warnings: list[str] = []

    base_rom = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
    if not base_rom.exists():
        errors.append(f"missing base ROM: {rel(base_rom)}")
    elif md5(base_rom) != summary["base_md5"]:
        errors.append(f"base ROM MD5 mismatch: expected {summary['base_md5']}, got {md5(base_rom)}")

    try:
        find_fceux(None)
    except FileNotFoundError as exc:
        errors.append(str(exc))

    target_rom = resolve_repo_path(action["rom_to_open"])
    if not target_rom.exists():
        errors.append(f"missing target ROM: {rel(target_rom)}")
    elif action.get("phase") == "primary_v042_visual_review" and md5(target_rom) != summary["primary_candidate_md5"]:
        errors.append(f"target ROM MD5 mismatch: expected {summary['primary_candidate_md5']}, got {md5(target_rom)}")

    watcher = resolve_repo_path(action["watcher_lua"])
    if not watcher.exists():
        errors.append(f"missing watcher Lua: {rel(watcher)}")

    if not action.get("record_visual_review"):
        warnings.append("next action has no record_visual_review command")
    if isinstance(current_visual_task, dict) and current_visual_task:
        task_summary = current_visual_task.get("summary", {})
        task_target = task_summary.get("target") if isinstance(task_summary, dict) else ""
        if task_target and task_target != action.get("target"):
            warnings.append(f"current visual task target {task_target} does not match next action {action.get('target')}")

    return errors, warnings


def main() -> int:
    context = load_next_manual_context()
    action = context["action"]
    if not isinstance(action, dict):
        print("OK: no pending manual FCEUX action.")
        return 0

    errors, warnings = validate_next_action(context)

    try:
        fceux = find_fceux(None)
    except FileNotFoundError as exc:
        fceux = None
        errors.append(str(exc))

    target_rom = resolve_repo_path(action["rom_to_open"])
    watcher = resolve_repo_path(action["watcher_lua"])
    current_visual_task = context.get("current_visual_task", {})
    task_summary = current_visual_task.get("summary", {}) if isinstance(current_visual_task, dict) else {}
    task_evidence = (
        current_visual_task.get("existing_auto_input_evidence", {}) if isinstance(current_visual_task, dict) else {}
    )

    print("Manual FCEUX preflight")
    print(f"- phase: {action['phase']}")
    print(f"- target: {action['target']} / {action['group']}")
    print(f"- hint: {action['screen_hint']}")
    print(f"- fceux: {rel(fceux) if fceux else '[missing]'}")
    print(f"- target ROM: {rel(target_rom)}")
    print(f"- watcher Lua: {rel(watcher)}")
    if action.get("record_visual_review"):
        print(f"- record command: {action['record_visual_review']}")
    if task_summary:
        print("- current visual task:")
        print(f"  decision: {task_summary.get('decision', '')}")
        print(f"  required screen: {task_summary.get('required_screen', '')}")
        print(f"  existing auto-input context: {task_summary.get('auto_input_context_status', '')}")
        if task_evidence.get("context_rejection_reason"):
            print(f"  why existing PNG is not enough: {task_evidence['context_rejection_reason']}")
    print("- launch helper:")
    print("  python " + " ".join(launch_command(action)))

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    print("OK: next manual FCEUX capture inputs are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

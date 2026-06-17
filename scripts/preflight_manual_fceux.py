#!/usr/bin/env python3
"""Check whether the next manual FCEUX capture is ready to run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from run_fceux_lua_analysis import find_fceux
from rom_utils import REPO_ROOT


NEXT_MANUAL_RUN = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
MANIFEST = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"


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


def main() -> int:
    manifest = load_json(MANIFEST)
    next_run = load_json(NEXT_MANUAL_RUN)
    action = next_run.get("next_action")
    if not isinstance(action, dict):
        print("OK: no pending manual FCEUX action.")
        return 0

    summary = manifest["summary"]
    errors: list[str] = []
    warnings: list[str] = []

    base_rom = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
    if not base_rom.exists():
        errors.append(f"missing base ROM: {rel(base_rom)}")
    elif md5(base_rom) != summary["base_md5"]:
        errors.append(f"base ROM MD5 mismatch: expected {summary['base_md5']}, got {md5(base_rom)}")

    try:
        fceux = find_fceux(None)
    except FileNotFoundError as exc:
        fceux = None
        errors.append(str(exc))

    target_rom = resolve_repo_path(action["rom_to_open"])
    if not target_rom.exists():
        errors.append(f"missing target ROM: {rel(target_rom)}")
    elif action.get("phase") == "primary_v042_visual_review" and md5(target_rom) != summary["primary_candidate_md5"]:
        errors.append(f"target ROM MD5 mismatch: expected {summary['primary_candidate_md5']}, got {md5(target_rom)}")

    watcher = resolve_repo_path(action["watcher_lua"])
    if not watcher.exists():
        errors.append(f"missing watcher Lua: {rel(watcher)}")

    record_command = action.get("record_visual_review")
    if not record_command:
        warnings.append("next action has no record_visual_review command")

    print("Manual FCEUX preflight")
    print(f"- phase: {action['phase']}")
    print(f"- target: {action['target']} / {action['group']}")
    print(f"- hint: {action['screen_hint']}")
    print(f"- fceux: {rel(fceux) if fceux else '[missing]'}")
    print(f"- target ROM: {rel(target_rom)}")
    print(f"- watcher Lua: {rel(watcher)}")
    if record_command:
        print(f"- record command: {record_command}")
    print("- launch helper:")
    print(
        "  python scripts/run_fceux_lua_analysis.py "
        f"--rom {rel(target_rom)} --lua-script {rel(watcher)} "
        "--timeout 600 --stop-after-manual-dump "
        "--final-output rom_analysis/fceux_manual_launch --clean-output --no-dump-hex --no-dump-bin"
    )

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

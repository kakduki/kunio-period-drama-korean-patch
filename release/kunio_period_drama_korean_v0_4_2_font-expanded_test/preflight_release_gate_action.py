#!/usr/bin/env python3
"""Validate the current release gate action plan before running evidence tasks."""

from __future__ import annotations

import json
import shlex
from pathlib import Path

try:
    from rom_utils import REPO_ROOT
except ModuleNotFoundError:
    REPO_ROOT = Path(__file__).resolve().parent


BUNDLE_MODE = (REPO_ROOT / "candidate_pipeline").is_dir() and not (REPO_ROOT / "rom_analysis").exists()


def first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


ACTION_PLAN = first_existing(
    REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "release_gate_action_plan.json",
    REPO_ROOT / "candidate_pipeline" / "release_gate_action_plan.json",
)
PADDING_MATRIX = first_existing(
    REPO_ROOT / "rom_analysis" / "candidate_pipeline" / "padding_experiment_matrix.json",
    REPO_ROOT / "candidate_pipeline" / "padding_experiment_matrix.json",
)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def resolve_repo_path(raw: object) -> Path:
    path = Path(str(raw))
    if not path.is_absolute():
        path = REPO_ROOT / path
    if path.exists() or not BUNDLE_MODE:
        return path

    text = str(raw).replace("\\", "/")
    bundle_alternates: list[Path] = []
    for prefix, replacement in [
        ("scripts/", ""),
        ("rom_analysis/candidate_pipeline/", "candidate_pipeline/"),
    ]:
        if text.startswith(prefix):
            bundle_alternates.append(REPO_ROOT / replacement / text[len(prefix) :])
    for alternate in bundle_alternates:
        if alternate.exists():
            return alternate
    return path


def command_script(command: object) -> Path | None:
    text = str(command).strip()
    if not text:
        return None
    parts = shlex.split(text, posix=False)
    if len(parts) < 2 or parts[0].lower() not in {"python", "py"}:
        return None
    return resolve_repo_path(parts[1])


def validate_action(action: dict[str, object], padding_v05_count: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    gate = str(action.get("gate", ""))
    phase = str(action.get("phase", ""))

    for required in ["priority", "gate", "status", "failure_class", "action", "target", "phase", "command", "evidence_needed"]:
        if not action.get(required):
            errors.append(f"{gate or phase}: missing action field {required}")

    rom_raw = str(action.get("rom_to_open", ""))
    if rom_raw and "<strategy>" not in rom_raw:
        rom_path = resolve_repo_path(rom_raw)
        if not rom_path.exists():
            if BUNDLE_MODE and rom_path.suffix.lower() == ".nes":
                warnings.append(f"{gate}: bundle intentionally omits ROM input {rel(rom_path)}")
            else:
                errors.append(f"{gate}: missing ROM input {rel(rom_path)}")
    elif phase == "padding_rule_acceptance" and padding_v05_count <= 0:
        errors.append(f"{gate}: no v05 padding strategies are available")

    watcher_raw = str(action.get("watcher_lua", ""))
    if watcher_raw and "<strategy>" not in watcher_raw:
        watcher = resolve_repo_path(watcher_raw)
        if not watcher.exists():
            errors.append(f"{gate}: missing watcher Lua {rel(watcher)}")

    script = command_script(action.get("command", ""))
    if script is None:
        warnings.append(f"{gate}: command is not a simple python script invocation")
    elif not script.exists():
        errors.append(f"{gate}: command script missing {rel(script)}")

    refresh = str(action.get("refresh", "")).strip()
    if refresh:
        for command in [part.strip() for part in refresh.split(";") if part.strip()]:
            refresh_script = command_script(command)
            if refresh_script is not None and not refresh_script.exists():
                errors.append(f"{gate}: refresh script missing {rel(refresh_script)}")

    return errors, warnings


def main() -> int:
    plan = load_json(ACTION_PLAN)
    padding = load_json(PADDING_MATRIX)
    actions = plan.get("actions", [])
    padding_v05_count = sum(
        1
        for row in padding.get("rows", [])
        if row.get("experiment_set") == "v05-current-font-base"
    )

    errors: list[str] = []
    warnings: list[str] = []
    if not actions:
        errors.append("release gate action plan has no actions")
    priorities = [int(action.get("priority", 0)) for action in actions if isinstance(action, dict)]
    if priorities != sorted(priorities):
        errors.append(f"release gate action priorities are not sorted: {priorities}")

    for action in actions:
        if not isinstance(action, dict):
            errors.append(f"invalid action row: {action!r}")
            continue
        action_errors, action_warnings = validate_action(action, padding_v05_count)
        errors.extend(action_errors)
        warnings.extend(action_warnings)

    print("Release gate action preflight")
    print(f"- mode: {'bundle' if BUNDLE_MODE else 'repository'}")
    print(f"- action plan: {rel(ACTION_PLAN)}")
    print(f"- actions: {len(actions)}")
    print(f"- first gate: {actions[0].get('gate') if actions and isinstance(actions[0], dict) else 'none'}")
    print(f"- padding v05 strategies: {padding_v05_count}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("OK: release gate action plan inputs are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

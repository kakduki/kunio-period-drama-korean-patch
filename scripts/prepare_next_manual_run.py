#!/usr/bin/env python3
"""Print the exact next manual FCEUX capture setup."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def find_root() -> Path:
    here = Path(__file__).resolve()
    candidates = [here.parents[1], here.parent]
    for candidate in candidates:
        if (candidate / "rom_analysis" / "next_manual_run.json").exists():
            return candidate
        if (candidate / "next_manual_run.json").exists():
            return candidate
    return here.parents[1]


ROOT = find_root()
NEXT_MANUAL_RUN = (
    ROOT / "rom_analysis" / "next_manual_run.json"
    if (ROOT / "rom_analysis" / "next_manual_run.json").exists()
    else ROOT / "next_manual_run.json"
)
CURRENT_PRIMARY_VISUAL_TASK = (
    ROOT / "rom_analysis" / "current_primary_visual_task.json"
    if (ROOT / "rom_analysis" / "current_primary_visual_task.json").exists()
    else ROOT / "current_primary_visual_task.json"
)


def rel_to_abs(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def load_next_action(path: Path) -> dict[str, object] | None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    action = payload.get("next_action")
    return action if isinstance(action, dict) else None


def load_current_visual_task() -> dict[str, object]:
    if not CURRENT_PRIMARY_VISUAL_TASK.exists():
        return {}
    return json.loads(CURRENT_PRIMARY_VISUAL_TASK.read_text(encoding="utf-8"))


def format_path(path: Path) -> str:
    if path.exists():
        return str(path)
    return f"{path}  [missing]"


def make_summary(action: dict[str, object], *, current_visual_task: dict[str, object], powershell: bool) -> str:
    rom = rel_to_abs(str(action["rom_to_open"]))
    watcher = rel_to_abs(str(action["watcher_lua"]))
    after_capture = [str(command) for command in action.get("after_capture", [])]
    record_visual_review = str(action.get("record_visual_review", ""))
    confirm_command = ""
    if action.get("phase") == "primary_v042_visual_review":
        confirm_command = (
            "python scripts/confirm_next_primary_visual.py --confirm-visible "
            f"--screen-context \"{action['screen_hint']} visible\""
        )
    elif record_visual_review:
        confirm_command = record_visual_review
    task_summary = current_visual_task.get("summary", {}) if isinstance(current_visual_task, dict) else {}
    task_evidence = (
        current_visual_task.get("existing_auto_input_evidence", {}) if isinstance(current_visual_task, dict) else {}
    )
    lines = [
        "Next manual FCEUX capture",
        "",
        f"Phase: {action['phase']}",
        f"Target: {action['target']}",
        f"Group: {action['group']}",
        f"Hint: {action['screen_hint']}",
        "",
        f"Open ROM: {format_path(rom)}",
        f"Run Lua:  {format_path(watcher)}",
        "",
        "Launch helper:",
        "- python scripts/run_next_manual_fceux.py",
        "",
        "Important:",
        "- This is a manual capture step; it does not autoplay through the game.",
        "- Waiting on the title/opening screen will not create useful patch evidence.",
    ]
    if task_summary:
        lines += [
            f"- Required screen: {task_summary.get('required_screen', '')}",
            f"- Existing auto-input context: {task_summary.get('auto_input_context_status', '')}",
        ]
        if task_evidence.get("context_rejection_reason"):
            lines.append(f"- Existing PNG is not enough: {task_evidence['context_rejection_reason']}")
    lines += [
        "",
        "At the target screen:",
        "- Press D to save the dump.",
        "- Press Q to stop the watcher.",
        "- If the screen is still title/opening, stop and fix manual controls first.",
        "",
        "If the visible screen matches the target, record visual review:",
    ]
    if confirm_command:
        lines.append(f"- {confirm_command}")
    else:
        lines.append("- No visual-review command recorded for this action.")
    lines += [
        "",
        "After capture if you ran FCEUX/Lua directly instead of the launcher:",
    ]
    lines.extend(f"- {command}" for command in after_capture)
    if powershell:
        lines += [
            "",
            "PowerShell from repository root:",
            f"Set-Location -LiteralPath '{ROOT}'",
            "python scripts/run_next_manual_fceux.py",
        ]
        if confirm_command:
            lines.append(confirm_command)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(NEXT_MANUAL_RUN), help="Path to next_manual_run.json.")
    parser.add_argument("--powershell", action="store_true", help="Also print repository-root PowerShell commands.")
    args = parser.parse_args()

    source = rel_to_abs(args.source)
    action = load_next_action(source)
    if not action:
        print("No pending manual FCEUX action.")
        return 0

    print(make_summary(action, current_visual_task=load_current_visual_task(), powershell=args.powershell), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

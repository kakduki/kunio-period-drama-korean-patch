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


def rel_to_abs(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def load_next_action(path: Path) -> dict[str, object] | None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    action = payload.get("next_action")
    return action if isinstance(action, dict) else None


def format_path(path: Path) -> str:
    if path.exists():
        return str(path)
    return f"{path}  [missing]"


def make_summary(action: dict[str, object], *, powershell: bool) -> str:
    rom = rel_to_abs(str(action["rom_to_open"]))
    watcher = rel_to_abs(str(action["watcher_lua"]))
    after_capture = [str(command) for command in action.get("after_capture", [])]
    record_visual_review = str(action.get("record_visual_review", ""))
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
        "At the target screen:",
        "- Press D to save the dump.",
        "- Press Q to stop the watcher.",
        "- If the screen is still title/opening, stop and fix manual controls first.",
        "",
        "If the visible screen matches the target, record visual review:",
    ]
    if record_visual_review:
        lines.append(f"- {record_visual_review}")
    else:
        lines.append("- No visual-review command recorded for this action.")
    lines += [
        "",
        "After capture:",
    ]
    lines.extend(f"- {command}" for command in after_capture)
    if powershell:
        lines += [
            "",
            "PowerShell from repository root:",
            f"Set-Location -LiteralPath '{ROOT}'",
        ]
        if record_visual_review:
            lines.append(record_visual_review)
        lines.extend(after_capture)
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

    print(make_summary(action, powershell=args.powershell), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

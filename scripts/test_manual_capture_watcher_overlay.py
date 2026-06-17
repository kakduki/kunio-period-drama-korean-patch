#!/usr/bin/env python3
"""Check that manual FCEUX capture watchers discourage blind waiting."""

from __future__ import annotations

from rom_utils import REPO_ROOT


WATCHER = REPO_ROOT / "lua" / "kunio_manual_capture_watch.lua"


def main() -> int:
    text = WATCHER.read_text(encoding="utf-8")
    required = [
        "Manual play required",
        "this does not press Start",
        "D=dump current screen",
        "Q=stop",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise SystemExit(f"manual capture watcher overlay missing: {', '.join(missing)}")
    print("OK: manual capture watcher overlay explains manual control and dump keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

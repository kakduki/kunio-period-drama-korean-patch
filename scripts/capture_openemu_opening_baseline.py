#!/usr/bin/env python3
"""Retired opening-menu capture routine.

It is retained only as historical tooling. The project policy prohibits using
opening-menu screenshots as Korean text-target evidence; use the static English
reference correlation first, then a debugger-capable trace when available.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def window_rect(title: str) -> tuple[int, int, int, int]:
    script = f'''tell application "System Events"
    tell process "OpenEmu"
        set frontmost to true
        delay 1
        set targetWindow to window "{title}"
        set p to position of targetWindow
        set s to size of targetWindow
        return (item 1 of p as text) & "," & (item 2 of p as text) & "," & (item 1 of s as text) & "," & (item 2 of s as text)
    end tell
end tell'''
    raw = run("/usr/bin/osascript", "-e", script)
    try:
        x, y, width, height = (int(part.strip()) for part in raw.split(","))
    except ValueError as exc:
        raise RuntimeError(f"unexpected OpenEmu window geometry: {raw!r}") from exc
    if width < 200 or height < 150:
        raise RuntimeError(f"implausible OpenEmu window geometry: {raw!r}")
    return x, y, width, height


def image_dimensions(path: Path) -> dict[str, int]:
    raw = run("/usr/bin/sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path))
    values = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key.strip() in {"pixelWidth", "pixelHeight"}:
                values[key.strip()] = int(value.strip())
    return {"width": values["pixelWidth"], "height": values["pixelHeight"]}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(path: Path, rect: tuple[int, int, int, int]) -> dict[str, object]:
    x, y, width, height = rect
    run("/usr/sbin/screencapture", "-x", "-R", f"{x},{y},{width},{height}", str(path))
    return {
        "file": path.name,
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "window_rect_points": {"x": x, "y": y, "width": width, "height": height},
        "image_pixels": image_dimensions(path),
        "sha256": digest(path),
    }


def main() -> int:
    raise SystemExit(
        "RETIRED: opening-menu captures are prohibited as translation evidence. "
        "Run scripts/analyze_english_reference_runs.py and "
        "scripts/correlate_korean_targets_to_english_reference.py instead."
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(exc.output, file=sys.stderr)
        raise

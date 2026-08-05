#!/usr/bin/env python3
"""Launch FCEUX and the Korean translation overlay for manual play.

Unlike the bounded analysis launcher, this command does not inject controller
input and does not stop after a frame budget. Close FCEUX to stop the overlay.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_fceux_lua_analysis import find_fceux, stage_fceux  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True, help="Japanese base ROM")
    parser.add_argument("--translator-command", help="Optional command receiving one JSON event on stdin")
    parser.add_argument("--fceux", type=Path, help="Optional FCEUX executable")
    parser.add_argument("--poll-ms", type=int, default=250)
    args = parser.parse_args()

    rom = args.rom.expanduser().resolve()
    if not rom.is_file():
        raise SystemExit(f"ROM not found: {rom}")
    lua_source = ROOT / "lua" / "kunio_translation_overlay.lua"
    targets_source = ROOT / "lua" / "kunio_translation_overlay_targets.lua"
    fceux = stage_fceux(find_fceux(args.fceux))
    workdir = fceux.parent
    ascii_rom = workdir / "rom.nes"
    ascii_lua = workdir / lua_source.name
    ascii_targets = workdir / targets_source.name
    shutil.copy2(rom, ascii_rom)
    shutil.copy2(lua_source, ascii_lua)
    shutil.copy2(targets_source, ascii_targets)

    output_dir = Path(tempfile.mkdtemp(prefix="kunio_realtime_overlay_"))
    events = output_dir / "events.tsv"
    draft_log = ROOT / "rom_analysis" / "realtime_overlay" / "manual_drafts.tsv"
    env = os.environ.copy()
    env.update({
        "KUNIO_OVERLAY_OUTPUT": str(output_dir),
        "KUNIO_OVERLAY_TARGETS_LUA": ascii_targets.name,
        "KUNIO_OVERLAY_DRIVE": "0",
        "KUNIO_OVERLAY_INTERACTIVE": "1",
    })
    fceux_proc = subprocess.Popen(
        [str(fceux), "--loadlua", ascii_lua.name, "--sound", "0", ascii_rom.name],
        cwd=workdir,
        env=env,
    )
    overlay_cmd = [
        sys.executable,
        str(ROOT / "tools" / "realtime_translation_overlay.py"),
        "--events", str(events),
        "--cache", str(ROOT / "translation" / "realtime_overlay.csv"),
        "--draft-log", str(draft_log),
        "--poll-ms", str(args.poll_ms),
    ]
    if args.translator_command:
        overlay_cmd.extend(["--translator-command", args.translator_command])
    overlay_proc = subprocess.Popen(overlay_cmd, cwd=ROOT)
    print("FCEUX manual-play overlay started.")
    print(f"Event log: {events}")
    print("Close FCEUX to stop the translation window.")
    try:
        while fceux_proc.poll() is None:
            time.sleep(0.5)
    finally:
        if overlay_proc.poll() is None:
            overlay_proc.terminate()
            try:
                overlay_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                overlay_proc.kill()
                overlay_proc.wait(timeout=5)
    return fceux_proc.returncode or 0


if __name__ == "__main__":
    raise SystemExit(main())
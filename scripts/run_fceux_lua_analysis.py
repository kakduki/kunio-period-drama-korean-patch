"""Launch FCEUX with the Kunio Lua analysis script.

This helper keeps FCEUX-facing paths ASCII-only where possible, because some
Windows FCEUX builds mishandle non-ASCII working directories in config files.
The Lua output is collected under tools/fceux_lua_output first, then mirrored
back into rom_analysis/fceux_lua after the emulator exits or the timeout fires.
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
DEFAULT_QFCEUX = ROOT / "tools" / "fceux-2.6.6-win64-QtSDL" / "bin" / "qfceux.exe"
DEFAULT_FCEUX = ROOT / "tools" / "fceux-2.6.6-win64" / "fceux64.exe"
LUA_SCRIPT = ROOT / "lua" / "kunio_auto_dump.lua"
FINAL_OUTPUT = ROOT / "rom_analysis" / "fceux_lua"
STAGED_FCEUX = Path(tempfile.gettempdir()) / "kunio_fceux_ascii_bin"


def find_rom() -> Path:
    rom_dir = ROOT / "rom"
    matches = sorted(rom_dir.glob("*.nes"))
    if not matches:
        raise FileNotFoundError("No .nes file found in rom/. Put the game ROM there first.")
    return matches[0]


def find_fceux(explicit: str | None) -> Path:
    if explicit:
        exe = Path(explicit).expanduser().resolve()
        if not exe.exists():
            raise FileNotFoundError(f"FCEUX executable not found: {exe}")
        return exe

    for candidate in (DEFAULT_QFCEUX, DEFAULT_FCEUX):
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "FCEUX executable was not found under tools/. "
        "Pass --fceux C:\\path\\to\\qfceux.exe or install/extract FCEUX there."
    )


def copytree_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        return
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def stage_fceux(exe: Path) -> Path:
    """Copy FCEUX beside ASCII-only runtime files.

    FCEUX 2.6.6 on Windows can launch from a non-ASCII path, but Lua loading is
    unreliable there. Running from %TEMP% avoids mojibake in the Lua loader.
    """

    if STAGED_FCEUX.exists():
        shutil.rmtree(STAGED_FCEUX)
    shutil.copytree(exe.parent, STAGED_FCEUX)
    staged_exe = STAGED_FCEUX / exe.name
    if not staged_exe.exists():
        raise FileNotFoundError(f"Staged FCEUX executable was not copied: {staged_exe}")
    return staged_exe


def update_cfg(exe: Path, lua_script_name: str, output_dir_name: str) -> None:
    cfg = exe.parent / "fceux.cfg"
    if not cfg.exists():
        return

    wanted = {
        "SDL.AutoOpenDebugger": "1",
        "SDL.DebugAutoStartTraceLogger": "1",
        "SDL.TraceLogSaveToFile": "1",
        "SDL.TraceLogBankNumber": "1",
        "SDL.TraceLogFrameCount": "1",
        "SDL.TraceLogInstructionCount": "1",
        "SDL.TraceLogCycleCount": "1",
        "SDL.OpenGL": "0",
        "SDL.XResolution": "512",
        "SDL.YResolution": "480",
        "SDL.LuaScript": lua_script_name,
        "SDL.LastLoadLua": lua_script_name,
        "SDL.TraceLogSaveFilePath": output_dir_name + "/fceux_trace.log",
    }

    lines = cfg.read_text(encoding="utf-8", errors="replace").splitlines()
    seen: set[str] = set()
    new_lines: list[str] = []

    for line in lines:
        if "=" not in line:
            new_lines.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in wanted:
            new_lines.append(f"{key} = {wanted[key]}")
            seen.add(key)
        else:
            new_lines.append(line)

    for key, value in wanted.items():
        if key not in seen:
            new_lines.append(f"{key} = {value}")

    cfg.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def launch(args: argparse.Namespace) -> int:
    rom = Path(args.rom).expanduser().resolve() if args.rom else find_rom()
    source_exe = find_fceux(args.fceux)
    exe = stage_fceux(source_exe)
    fceux_workdir = exe.parent
    ascii_rom = fceux_workdir / "rom.nes"
    ascii_lua = fceux_workdir / "kunio_auto_dump.lua"
    ascii_output = fceux_workdir / "kunio_fceux_lua_output"

    ascii_output.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rom, ascii_rom)
    shutil.copy2(LUA_SCRIPT, ascii_lua)

    update_cfg(exe, ascii_lua.name, ascii_output.name)

    env = os.environ.copy()
    env["KUNIO_ANALYSIS_OUTPUT"] = ascii_output.name
    env["KUNIO_MAX_FRAMES"] = str(args.frames)
    env["KUNIO_SNAPSHOT_EVERY"] = str(args.snapshot_every)
    env["KUNIO_PPU_BURST_THRESHOLD"] = str(args.ppu_burst_threshold)

    cmd = [str(exe), "--loadlua", ascii_lua.name, "--sound", "0", ascii_rom.name]
    print("Launching:", " ".join(cmd))
    print("Lua script:", LUA_SCRIPT)
    print("FCEUX working dir:", fceux_workdir)
    print("Temporary output:", ascii_output)
    print("Final output:", FINAL_OUTPUT)

    proc = subprocess.Popen(cmd, cwd=fceux_workdir, env=env)
    deadline = time.monotonic() + args.timeout
    completed = False
    summary = ascii_output / "summary.tsv"

    try:
        while proc.poll() is None and time.monotonic() < deadline:
            if summary.exists() and "lua_done" in summary.read_text(encoding="utf-8", errors="ignore"):
                completed = True
                print("Lua script reported completion; stopping FCEUX.")
                proc.terminate()
                break
            time.sleep(1)
    finally:
        if proc.poll() is None:
            if not completed:
                print(f"Timeout reached ({args.timeout}s); stopping FCEUX.")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    copytree_contents(ascii_output, FINAL_OUTPUT)
    print("Copied Lua output into:", FINAL_OUTPUT)
    if completed:
        return 0
    return proc.returncode or 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", help="Path to the .nes ROM. Defaults to first rom/*.nes.")
    parser.add_argument("--fceux", help="Path to qfceux.exe or fceux64.exe.")
    parser.add_argument("--frames", type=int, default=7200, help="Frames to run in Lua.")
    parser.add_argument("--timeout", type=int, default=180, help="Seconds before stopping FCEUX.")
    parser.add_argument("--snapshot-every", type=int, default=300, help="Periodic dump interval in frames.")
    parser.add_argument("--ppu-burst-threshold", type=int, default=24, help="PPUDATA/PPUADDR writes per frame that trigger a dump.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(launch(parse_args(sys.argv[1:])))

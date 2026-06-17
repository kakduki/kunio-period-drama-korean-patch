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
DEFAULT_LUA_SCRIPT = ROOT / "lua" / "kunio_auto_dump.lua"
STAGED_FCEUX = Path(tempfile.gettempdir()) / "kunio_fceux_ascii_bin"
BLIND_AUTOPLAY_FRAME_CAP = 1800
BLIND_AUTOPLAY_TIMEOUT_CAP = 90


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


def find_lua_script(explicit: str | None) -> Path:
    lua_script = Path(explicit).expanduser() if explicit else DEFAULT_LUA_SCRIPT
    if not lua_script.is_absolute():
        lua_script = ROOT / lua_script
    lua_script = lua_script.resolve()
    if not lua_script.exists():
        raise FileNotFoundError(f"Lua script not found: {lua_script}")
    return lua_script


def resolve_optional_path(explicit: str | None) -> Path | None:
    if not explicit:
        return None
    path = Path(explicit).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path


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


def summary_final_reason(summary: Path) -> str | None:
    if not summary.exists():
        return None
    text = summary.read_text(encoding="utf-8", errors="ignore")
    for marker in ("lua_done", "stagnant_screen", "hit_limit"):
        if marker in text:
            return marker
    return None


def is_blind_autoplay(args: argparse.Namespace, lua_script: Path) -> bool:
    if args.target_lua:
        return False
    return lua_script.name in {"kunio_auto_dump.lua", "kunio_autoplay_watch.lua"}


def apply_blind_autoplay_budget(args: argparse.Namespace, lua_script: Path) -> None:
    if args.allow_long_autoplay or not is_blind_autoplay(args, lua_script):
        return
    if args.frames > BLIND_AUTOPLAY_FRAME_CAP:
        print(
            "Blind autoplay frame budget applied: "
            f"{args.frames} -> {BLIND_AUTOPLAY_FRAME_CAP}. "
            "Use --allow-long-autoplay only when a specific route is worth testing."
        )
        args.frames = BLIND_AUTOPLAY_FRAME_CAP
    if args.timeout > BLIND_AUTOPLAY_TIMEOUT_CAP:
        print(
            "Blind autoplay timeout budget applied: "
            f"{args.timeout}s -> {BLIND_AUTOPLAY_TIMEOUT_CAP}s."
        )
        args.timeout = BLIND_AUTOPLAY_TIMEOUT_CAP


def print_manual_capture_hint(reason: str) -> None:
    if reason == "stagnant_screen":
        print(
            "Stagnant screen detected. Stop extending this autoplay run; "
            "open the target screen manually and run lua/kunio_manual_screen_dump.lua "
            "or lua/kunio_manual_broad_scan_dump.lua."
        )
    elif reason == "timeout":
        print(
            "No Lua completion marker was seen before timeout. If the emulator is still "
            "on the opening/title screen, switch to manual capture instead of increasing frames."
        )


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
    lua_script = find_lua_script(args.lua_script)
    apply_blind_autoplay_budget(args, lua_script)
    final_output = Path(args.final_output).expanduser().resolve()
    exe = stage_fceux(source_exe)
    fceux_workdir = exe.parent
    ascii_rom = fceux_workdir / "rom.nes"
    ascii_lua = fceux_workdir / lua_script.name
    ascii_output = fceux_workdir / "kunio_fceux_lua_output"
    target_lua = resolve_optional_path(args.target_lua)

    if ascii_output.exists():
        shutil.rmtree(ascii_output)
    ascii_output.mkdir(parents=True, exist_ok=True)
    if args.clean_output and final_output.exists():
        shutil.rmtree(final_output)
    final_output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rom, ascii_rom)
    shutil.copy2(lua_script, ascii_lua)
    lua_targets = lua_script.parent / "kunio_bank1_targets.lua"
    if lua_targets.exists():
        shutil.copy2(lua_targets, fceux_workdir / lua_targets.name)
    if target_lua:
        shutil.copy2(target_lua, fceux_workdir / target_lua.name)

    update_cfg(exe, ascii_lua.name, ascii_output.name)

    env = os.environ.copy()
    env["KUNIO_ANALYSIS_OUTPUT"] = ascii_output.name
    env["KUNIO_MAX_FRAMES"] = str(args.frames)
    env["KUNIO_SNAPSHOT_EVERY"] = str(args.snapshot_every)
    env["KUNIO_PPU_BURST_THRESHOLD"] = str(args.ppu_burst_threshold)
    env["KUNIO_DUMP_HEX"] = "1" if args.dump_hex else "0"
    env["KUNIO_DUMP_BIN"] = "1" if args.dump_bin else "0"
    env["KUNIO_HIT_LIMIT"] = str(args.hit_limit)
    env["KUNIO_STAGNATION_ABORT"] = "1" if args.stagnation_abort else "0"
    env["KUNIO_STAGNATION_MIN_FRAMES"] = str(args.stagnation_min_frames)
    env["KUNIO_STAGNATION_SAMPLES"] = str(args.stagnation_samples)
    if target_lua:
        env["KUNIO_TARGETS_LUA"] = target_lua.name

    cmd = [str(exe), "--loadlua", ascii_lua.name, "--sound", "0", ascii_rom.name]
    print("Launching:", " ".join(cmd))
    print("Lua script:", lua_script)
    print("FCEUX working dir:", fceux_workdir)
    print("Temporary output:", ascii_output)
    print("Final output:", final_output)

    proc = subprocess.Popen(cmd, cwd=fceux_workdir, env=env)
    deadline = time.monotonic() + args.timeout
    completed = False
    summary = ascii_output / "summary.tsv"

    try:
        while proc.poll() is None and time.monotonic() < deadline:
            final_reason = summary_final_reason(summary)
            if final_reason:
                completed = True
                print(f"Lua script reported {final_reason}; stopping FCEUX.")
                print_manual_capture_hint(final_reason)
                proc.terminate()
                break
            time.sleep(1)
    finally:
        if proc.poll() is None:
            if not completed:
                print(f"Timeout reached ({args.timeout}s); stopping FCEUX.")
                print_manual_capture_hint("timeout")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    copytree_contents(ascii_output, final_output)
    print("Copied Lua output into:", final_output)
    if completed:
        return 0
    return proc.returncode or 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", help="Path to the .nes ROM. Defaults to first rom/*.nes.")
    parser.add_argument("--fceux", help="Path to qfceux.exe or fceux64.exe.")
    parser.add_argument("--lua-script", default=str(DEFAULT_LUA_SCRIPT), help="Lua script to stage and run inside FCEUX.")
    parser.add_argument("--target-lua", help="Optional Lua target table copied beside the Lua script and exposed as KUNIO_TARGETS_LUA.")
    parser.add_argument("--frames", type=int, default=7200, help="Frames to run in Lua.")
    parser.add_argument("--timeout", type=int, default=180, help="Seconds before stopping FCEUX.")
    parser.add_argument("--allow-long-autoplay", action="store_true", help="Disable the short safety budget for untargeted autoplay runs.")
    parser.add_argument("--snapshot-every", type=int, default=300, help="Periodic dump interval in frames.")
    parser.add_argument("--ppu-burst-threshold", type=int, default=24, help="PPUDATA/PPUADDR writes per frame that trigger a dump.")
    parser.add_argument("--hit-limit", type=int, default=50000, help="Maximum read hits for watcher Lua scripts that support KUNIO_HIT_LIMIT.")
    parser.add_argument("--stagnation-abort", action=argparse.BooleanOptionalAction, default=True, help="Let supported Lua scripts stop early when the nametable appears unchanged for repeated samples.")
    parser.add_argument("--stagnation-min-frames", type=int, default=1800, help="Minimum frame before supported Lua scripts may stop for repeated unchanged-screen samples.")
    parser.add_argument("--stagnation-samples", type=int, default=4, help="Consecutive unchanged-screen samples required before supported Lua scripts stop early.")
    parser.add_argument("--final-output", default=str(ROOT / "rom_analysis" / "fceux_lua"), help="Directory where Lua output is mirrored after FCEUX exits.")
    parser.add_argument("--clean-output", action="store_true", help="Delete the final output directory before copying new results.")
    parser.add_argument("--dump-hex", action=argparse.BooleanOptionalAction, default=True, help="Write text hex dumps at snapshot frames.")
    parser.add_argument("--dump-bin", action=argparse.BooleanOptionalAction, default=True, help="Write raw binary dumps at snapshot frames.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(launch(parse_args(sys.argv[1:])))

# FCEUX Lua automation attempts

Date: 2026-06-15

## Goal

Run `lua/kunio_auto_dump.lua` inside FCEUX so the emulator can automatically
advance the game and save frame-indexed memory/PPU-oriented dumps.

## What was prepared

- `lua/kunio_auto_dump.lua`: Lua script for automatic input, periodic dumps,
  and `$2006/$2007` write-event capture when supported.
- `scripts/run_fceux_lua_analysis.py`: Windows launcher that copies the ROM and
  Lua script beside FCEUX, uses ASCII-only runtime paths, and mirrors output
  back into `rom_analysis/fceux_lua/`.
- FCEUX Qt/SDL 2.6.6 was extracted locally under ignored `tools/`.
- The launcher configures trace-related `fceux.cfg` keys and uses FCEUX's
  discovered `--loadlua` command-line option.

## Attempts

1. `SDL.LuaScript` / `SDL.LastLoadLua` config autoload:
   - FCEUX launched with the ROM.
   - No `summary.tsv`, `events.tsv`, or dump files were created.

2. Qt/SDL FCEUX `--loadlua kunio_auto_dump.lua --sound 0 rom.nes`:
   - FCEUX launched and ran until the test timeout.
   - No Lua output files were created.

3. Qt/SDL FCEUX `--loadlua=kunio_auto_dump.lua --sound 0 rom.nes`:
   - FCEUX launched and ran until the test timeout.
   - No Lua output files were created.

4. Qt/SDL FCEUX with option order changed to `--sound 0 rom.nes --loadlua kunio_auto_dump.lua`:
   - FCEUX launched and ran until the test timeout.
   - No Lua output files were created.

5. Classic Win64 FCEUX `--loadlua kunio_auto_dump.lua rom.nes`:
   - FCEUX launched and ran until the test timeout.
   - No Lua output files were created.

6. Windows SendKeys fallback from the repository path:
   - FCEUX launched with the ROM.
   - Sent `Ctrl+L`, pasted a temporary Lua script path, and pressed Enter.
   - No Lua output files were created.

7. Minimal Lua smoke test from `%TEMP%\kunio_fceux_ascii_bin`:
   - Copied the Qt/SDL FCEUX directory, ROM, and a tiny Lua script into an
     ASCII-only temp path.
   - `qfceux.exe --loadlua codex_lua_smoke.lua --sound 0 rom.nes` created
     `codex_lua_smoke_result.txt`.
   - This proved the blocker was the non-ASCII repository path, not the Lua API.

8. Full automation from `%TEMP%\kunio_fceux_ascii_bin`:
   - Updated `scripts/run_fceux_lua_analysis.py` to stage FCEUX in `%TEMP%`.
   - Ran `python scripts/run_fceux_lua_analysis.py --frames 900 --timeout 90 --snapshot-every 180`.
   - Lua completed and generated `summary.tsv`, `events.tsv`, and frame dumps
     under `rom_analysis/fceux_lua/`.

## Current status

The Lua script now runs automatically when FCEUX is staged under an ASCII-only
temp directory. The current verified run captured 900 frames and wrote 14 dump
sets. Strong runtime PPU burst frames include `33`, `95`, `125`, `233`, `284`,
`314`, and `653`; frame `314` tracked a nametable-region address around
`$20A1`.

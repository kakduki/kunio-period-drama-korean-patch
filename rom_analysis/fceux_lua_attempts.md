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

6. Windows SendKeys fallback:
   - FCEUX launched with the ROM.
   - Sent `Ctrl+L`, pasted a temporary Lua script path, and pressed Enter.
   - No Lua output files were created.

## Current status

The Lua script and launcher are ready, but this Codex desktop session did not
successfully prove that FCEUX loaded the Lua script. The next reliable manual
step is to open FCEUX visibly, open the ROM, choose `File > Lua > New Lua Script
Window` or `File > Run Lua Script`, and select `lua/kunio_auto_dump.lua`.

If the overlay text appears, let the script run until it pauses or until enough
text/menu screens have appeared. The expected output location is
`rom_analysis/fceux_lua/`.

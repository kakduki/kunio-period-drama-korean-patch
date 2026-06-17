# FCEUX Lua automation

This repository includes a Lua automation script for Windows FCEUX runtime
analysis:

- `lua/kunio_auto_dump.lua`
- `scripts/run_fceux_lua_analysis.py`

The script opens after the ROM is loaded, advances the game with conservative
controller input, samples likely text-rendering moments, and writes dumps into
`rom_analysis/fceux_lua/`.

## Run from Codex or PowerShell

Put the ROM in `rom/` first, then run:

```powershell
python scripts/run_fceux_lua_analysis.py
```

Useful options:

```powershell
python scripts/run_fceux_lua_analysis.py --frames 10800 --timeout 240
python scripts/run_fceux_lua_analysis.py --fceux C:\path\to\qfceux.exe
python scripts/run_fceux_lua_analysis.py --rom C:\path\to\game.nes
python scripts/run_fceux_lua_analysis.py --stagnation-min-frames 1800 --stagnation-samples 4
```

The launcher copies the selected FCEUX directory to an ASCII-only staging path
under `%TEMP%\kunio_fceux_ascii_bin`, then copies the ROM and Lua script beside
that staged executable. This avoids Windows path encoding issues that prevent
FCEUX 2.6.6 from loading Lua scripts from the repository's Korean path. When
the Lua script reports completion, the launcher stops FCEUX and mirrors the
output to:

```text
rom_analysis/fceux_lua/
```

The supported autoplay Lua scripts also sample the visible nametable. If the
same screen repeats after the configured minimum frame count, the script writes
`stagnant_screen` and the launcher stops FCEUX. Treat that as "the bot is stuck
on the same opening/menu screen", not as useful gameplay coverage. Do not
extend the same run for hours; manually reach the target screen and run the
one-shot manual dump script instead.

## If Lua does not autoload

The launcher uses FCEUX's `--loadlua` option from the ASCII staging directory.
If the emulator opens without the overlay text:

1. Keep the ROM open.
2. Open `File > Lua > New Lua Script Window` or `File > Run Lua Script`.
3. Select `lua/kunio_auto_dump.lua`.
4. Let it run until it pauses or until the launcher timeout stops FCEUX.

## Output files

- `summary.tsv`: frame, trigger reason, PPU-write count, last tracked PPU address, dump stem.
- `events.tsv`: `$2006/$2007` write events when the running FCEUX build supports Lua write callbacks.
- `frame_*_cpu_ram.txt`: CPU RAM hex dump.
- `frame_*_sram_6000_7fff.txt`: SRAM/expanded CPU address range dump.
- `frame_*_nametable_2000_2fff.txt`: nametable-oriented dump, using the PPU domain when supported.
- `*.bin`: raw dumps, generated locally and ignored by git by default.

Final summary reasons:

- `lua_done`: the configured frame count completed.
- `hit_limit`: a read-watch script reached its configured hit budget.
- `stagnant_screen`: the visible nametable did not change across repeated
  samples; stop autoplay and switch to manual capture.

The important follow-up is to compare dump frames with the static candidates in
`rom_analysis/README.md`, especially the `$2006/$2007` writer region and the
bank16 `1` text-like candidate offsets.

Note: the launcher enables trace-related FCEUX config keys, but the verified
automatic artifact is the Lua event trace (`events.tsv`). In the tested FCEUX
2.6.6 Qt/SDL build, the debugger Trace Logger did not emit `fceux_trace.log`
without manual debugger interaction.

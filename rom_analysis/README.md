# ROM analysis notes

## ROM identity

- File used locally: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Size: `262,160` bytes
- MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Mapper: MMC3 / mapper 4
- PRG ROM: `131,072` bytes
- CHR ROM: `131,072` bytes

## Generated files

- `extract_text_output.txt`: heuristic text/pointer scan
- `find_text_output.txt`: PRG text-like byte-region scan
- `analyze_rom_output.txt`: ASCII/SJIS scan and basic PRG summary
- `analyze_chr_output.txt`: CHR dump and fixed-bank dump
- `disasm_6502_output.txt`: rough 6502 fixed-bank disassembly scan, generated locally only and ignored by git
- `ppu_register_refs.txt`: static references to PPU registers
- `font_mapping_notes.md`: preliminary visual CHR bank 07 tile mapping
- `kana_pattern_scan.txt`: PRG scan for kana-like byte patterns based on the CHR bank 07 tile order
- `candidate_region_decode.txt`: tentative kana-offset decoding around the strongest PRG candidates
- `fceux_lua/summary.tsv`: frame-indexed summary from the FCEUX Lua automation, generated locally after running `scripts/run_fceux_lua_analysis.py`
- `fceux_lua/events.tsv`: `$2006/$2007` write events from the FCEUX Lua automation when the emulator build supports Lua write callbacks
- `fceux_lua_event_summary.md`: grouped summary of runtime `$2006/$2007` writes, highlighting nametable/text-rendering candidates
- `fceux_lua_nametable_reconstruction.md`: 32x30 nametable tile-grid reconstruction from `$2007` events for the strongest text/UI candidate frames
- `fceux_lua_long/summary.tsv`: 7,200-frame Lua automation summary, collected with bulky memory dumps disabled
- `fceux_lua_long/events.tsv`: 7,200-frame `$2006/$2007` runtime event log
- `fceux_lua_long_event_summary.md`: grouped event summary for the 7,200-frame run, starting after frame `900`
- `fceux_lua_long_nametable_reconstruction.md`: selected 32x30 nametable reconstructions from the strongest long-run non-zero tile-write candidates
- `chr/chr_dump.bin`: raw CHR ROM dump, generated locally only and ignored by git
- `chr/bank_fixed.txt`: fixed PRG-bank hex dump, generated locally only and ignored by git
- `font/chr_bank_##_8x8.png`: CHR banks rendered as 8x8 tiles, generated locally only and ignored by git
- `font/chr_bank_##_8x16.png`: CHR banks rendered as 8x16 tile pairs, generated locally only and ignored by git
- `font/chr_bank_##_*_labeled.png`: labeled tile sheets, generated locally only and ignored by git

## Findings so far

- Plain Shift-JIS extraction does not produce normal dialogue. The hits are mostly false positives from binary data, so the game likely uses a custom tile/code mapping rather than raw Shift-JIS strings.
- `font/chr_bank_07_8x16.png` is the strongest font candidate. It visibly contains kana, numerals, Latin letters, and symbols.
- After rendering bank 07 as `8x8`, the font block is clearer than the `8x16` view. Hiragana begins around tile `0x101`; numerals begin around `0x1C0`; Latin capitals begin around `0x1E1`.
- `font/chr_bank_06_8x16.png` also contains visible numerals/UI-like tiles, but it is more mixed with sprite/background data.
- Static PPU reference scanning found the most relevant nametable/text-output candidates around:
  - `$2006 PPUADDR`: `ROM+0x1D7FB` through `ROM+0x1D806`, bank 7, CPU approx `$97EB-$97F6`
  - `$2007 PPUDATA`: `ROM+0x1D712` through `ROM+0x1D7EB`, bank 7, CPU approx `$9702-$97DB`
  - Additional `$2007` writes at `ROM+0x1A2A2`, `0x1A2CB`, `0x1A2E4`, `0x1CEE2`, `0x1DDC3`, `0x1F2B9`, and `0x1FE02`
- Because this is MMC3, the static CPU addresses are approximate. FCEUX trace logs should be used to confirm the active bank and real call path.
- A first kana-pattern PRG scan did not find useful `direct-low-byte` matches, so CHR tile numbers are probably not stored directly as text bytes.
- The offset scan produced stronger candidates in bank16 `1`, especially:
  - `add=0x7C`, `katana` candidates around `ROM+0x05644`, `0x06295`, `0x0631C`, `0x0635A`
  - `add=0x82`, `chikara` candidates around `ROM+0x06605`, `0x066FB`, `0x06845`, `0x06B4A`, `0x071A4`
  - `add=0x93`, `raifu` candidates around `ROM+0x0736A`, `0x0739D`
- These offset hits are not proof of text data yet; short kana patterns can collide with code/data. They are useful FCEUX breakpoint/trace candidates.
- The candidate-region decoder makes the bank16 `1` candidates easier to inspect:
  - `add=0x7C` around `PRG+0x05630`, `0x06280`, and `0x06300` decodes visible `かたな` fragments.
  - `add=0x82` around `PRG+0x066E0` and `0x06830` decodes visible `ちから` fragments.
  - `add=0x93` around `PRG+0x07350` and `0x07380` decodes visible `らいふ` fragments.
- The bank16 `5` cluster around `PRG+0x17D30-0x17D80` repeatedly decodes `たから`/`ちから`, but the regular `00 00 FC/FD/FE` structure looks table-like. Treat it as a lower-confidence text candidate until FCEUX confirms reads during UI rendering.

## FCEUX Lua automation

The repository includes `lua/kunio_auto_dump.lua` and
`scripts/run_fceux_lua_analysis.py` to reduce manual GUI work. The launcher
stages FCEUX in an ASCII-only `%TEMP%` path, opens the ROM, runs the Lua script,
and mirrors generated dumps into `rom_analysis/fceux_lua/`.

Run:

```powershell
python scripts/run_fceux_lua_analysis.py --frames 10800 --timeout 240
```

If the Lua overlay does not appear in FCEUX, load `lua/kunio_auto_dump.lua`
manually from the FCEUX Lua menu while the ROM is open.

Verified run:

- Command: `python scripts/run_fceux_lua_analysis.py --frames 900 --timeout 90 --snapshot-every 180`
- Result: Lua completed automatically and saved 14 dump sets.
- Strong PPU burst frames: `33`, `95`, `125`, `233`, `284`, `314`, `653`
- Frame `314` is especially interesting because the tracked PPU address reached
  `$20A1`, a nametable-region address likely related to visible text/UI writes.
- FCEUX did not create `fceux_trace.log` in this run. The verified runtime trace
  artifact is `fceux_lua/events.tsv`, which records Lua-captured `$2006/$2007`
  writes instead of the debugger Trace Logger's full CPU instruction log.
- `scripts/analyze_fceux_lua_events.py` groups the Lua event log by frame and
  address range. It found that the first coarse PPU burst list was too broad:
  palette-only frames are less useful, while frame clusters `22-27` and
  `313-318` contain substantial nametable writes. Frame `314` remains the
  strongest current candidate, but frames `313`, `315`, `316`, `317`, and `318`
  should be inspected together because they appear to be one multi-frame screen
  composition sequence.
- `scripts/reconstruct_nametable_from_events.py` rebuilds 32x30 tile grids from
  `$2007` events. The reconstruction shows frame cluster `313-317` writing
  mostly to nametable rows `04-05`, while frames `339-361` update row `24` two
  cells at a time. This gives a text-file equivalent of the PPU Viewer for the
  automated run.
- A longer 7,200-frame event-only run reached additional UI/text-like clusters.
  Strong non-zero nametable candidates include frame groups `1020-1026`,
  `2903-2908`, `5184-5187`, `5464-5470`, plus smaller row updates at `6614`
  and `7091`. These are better next targets than palette-only bursts.

## Next FCEUX targets

FCEUX 2.6.6 Win64 was downloaded locally into `tools/`, which is ignored by git. In this Codex session the process launched, but no targetable GUI window handle appeared, so live Trace Logger automation could not be completed here.

Once FCEUX is available on the visible desktop:

1. Open the ROM.
2. Start `Debug > Trace Logger` and enable file logging.
3. Progress to a screen where dialogue/menu text appears.
4. In `Debug > PPU Viewer`, confirm that the visible font corresponds to CHR bank 07. Use the local ignored labeled sheet `font/chr_bank_07_8x8_labeled.png` for comparison.
5. In `Debug > Hex Editor` / debugger, watch writes to `$2006` and `$2007`.
6. Pay special attention to execution near CPU approx `$9702-$97DB` and `$97EB-$97F6`.
7. Also check whether reads near PRG bank16 `1`, ROM offsets `0x05640`, `0x06290`, `0x066E0`, `0x06830`, `0x07350`, and `0x07380` occur when item/status text appears.
8. Save the trace log, PPU screenshots, and any nametable/memory dumps into this `rom_analysis/` folder.

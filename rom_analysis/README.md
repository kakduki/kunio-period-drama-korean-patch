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
- `chr/chr_dump.bin`: raw CHR ROM dump, generated locally only and ignored by git
- `chr/bank_fixed.txt`: fixed PRG-bank hex dump, generated locally only and ignored by git
- `font/chr_bank_##_8x8.png`: CHR banks rendered as 8x8 tiles, generated locally only and ignored by git
- `font/chr_bank_##_8x16.png`: CHR banks rendered as 8x16 tile pairs, generated locally only and ignored by git

## Findings so far

- Plain Shift-JIS extraction does not produce normal dialogue. The hits are mostly false positives from binary data, so the game likely uses a custom tile/code mapping rather than raw Shift-JIS strings.
- `font/chr_bank_07_8x16.png` is the strongest font candidate. It visibly contains kana, numerals, Latin letters, and symbols.
- `font/chr_bank_06_8x16.png` also contains visible numerals/UI-like tiles, but it is more mixed with sprite/background data.
- Static PPU reference scanning found the most relevant nametable/text-output candidates around:
  - `$2006 PPUADDR`: `ROM+0x1D7FB` through `ROM+0x1D806`, bank 7, CPU approx `$97EB-$97F6`
  - `$2007 PPUDATA`: `ROM+0x1D712` through `ROM+0x1D7EB`, bank 7, CPU approx `$9702-$97DB`
  - Additional `$2007` writes at `ROM+0x1A2A2`, `0x1A2CB`, `0x1A2E4`, `0x1CEE2`, `0x1DDC3`, `0x1F2B9`, and `0x1FE02`
- Because this is MMC3, the static CPU addresses are approximate. FCEUX trace logs should be used to confirm the active bank and real call path.

## Next FCEUX targets

FCEUX was not found on this Windows machine during this run.

Once FCEUX is installed:

1. Open the ROM.
2. Start `Debug > Trace Logger` and enable file logging.
3. Progress to a screen where dialogue/menu text appears.
4. In `Debug > PPU Viewer`, confirm that the visible font corresponds to `font/chr_bank_07_8x16.png`.
5. In `Debug > Hex Editor` / debugger, watch writes to `$2006` and `$2007`.
6. Pay special attention to execution near CPU approx `$9702-$97DB` and `$97EB-$97F6`.
7. Save the trace log, PPU screenshots, and any nametable/memory dumps into this `rom_analysis/` folder.

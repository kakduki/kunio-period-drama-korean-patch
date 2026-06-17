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
- `chr_bank07_tile_map.json` / `chr_bank07_tile_map.md`: structured CHR bank 07 glyph map with tile indexes, ROM offsets, candidate `+0x7A` PRG bytes, and tile hashes
- `chr_bank07_patch_inventory.md` / `chr_bank07_patch_inventory.json`: current v0.1 Bank7 patch slot inventory, mapping original CHR tiles to patched glyph slots from `font/char_map.json`
- `korean_slot_allocation_plan.md` / `korean_slot_allocation_plan.json`: compact Korean glyph-to-CHR-slot plan for the current Bank 1 offset inventory, including planned `+0x7A` PRG bytes
- `prg_padding_options.md` / `prg_padding_options.json`: compares planned Korean PRG bytes against original candidate byte spans and classifies equal-length vs padding-risk replacements
- `kana_pattern_scan.txt`: PRG scan for kana-like byte patterns based on the CHR bank 07 tile order
- `candidate_region_decode.txt`: tentative kana-offset decoding around the strongest PRG candidates
- `bank1_text_block_map.md` / `bank1_text_block_map.json`: tentative `0xFF`-delimited block map for `ROM+0x05610-0x05810` under the `CHR tile = PRG byte + 0x7A` hypothesis, including structured block metadata and watch-range patch readiness
- `translation_offset_candidates.md`: translation-data-to-ROM candidate table for Bank 1, including exact `plus-0x7A` matches and lower-confidence shifted-offset hits
- `bank1_candidate_contexts.md`: focused Bank 1 candidate contexts with delimiter-bounded record ranges, CPU record addresses, and raw little-endian pointer references
- `bank1_watch_targets.json`: generated Bank 1 read-watch target list derived from `bank1_candidate_contexts.md`; the Lua copy is `lua/kunio_bank1_targets.lua`
- `bank1_offset_inventory.md` / `bank1_offset_inventory.json`: category-oriented Bank 1 offset inventory that merges static translation candidates, watch-range supplemental hits, and FCEUX read-watch evidence
- `fceux_lua/summary.tsv`: frame-indexed summary from the FCEUX Lua automation, generated locally after running `scripts/run_fceux_lua_analysis.py`
- `fceux_lua/events.tsv`: `$2006/$2007` write events from the FCEUX Lua automation when the emulator build supports Lua write callbacks
- `fceux_lua_event_summary.md`: grouped summary of runtime `$2006/$2007` writes, highlighting nametable/text-rendering candidates
- `fceux_lua_nametable_reconstruction.md`: 32x30 nametable tile-grid reconstruction from `$2007` events for the strongest text/UI candidate frames
- `fceux_lua_long/summary.tsv`: 7,200-frame Lua automation summary, collected with bulky memory dumps disabled
- `fceux_lua_long/events.tsv`: 7,200-frame `$2006/$2007` runtime event log
- `fceux_lua_long_event_summary.md`: grouped event summary for the 7,200-frame run, starting after frame `900`
- `fceux_lua_long_nametable_reconstruction.md`: selected 32x30 nametable reconstructions from the strongest long-run non-zero tile-write candidates
- `fceux_bank1_watch/summary.tsv`: optional Bank 1 read-watch run summary from `lua/kunio_bank1_watch.lua`
- `fceux_bank1_watch/bank1_reads.tsv`: optional CPU read hits for the Bank 1 candidate records, generated when the emulator build supports Lua read callbacks
- `fceux_bank1_watch_test_summary.md`: short 900-frame validation summary for the Bank 1 read watcher
- `fceux_ppu_watch/analysis.md`: first-pass PPU write watch analysis; useful for raw address/write frequency, but exact text matching is limited by same-frame contiguous-run grouping
- `fceux_ppu_watch/analysis_v2.md`: corrected PPU write analysis from `scripts/analyze_ppu_watch_v2.py`; reconstructs frame nametables, strips fill/attribute writes, and currently matches 5 of 36 generated Bank 1 targets
- `chr/chr_dump.bin`: raw CHR ROM dump, generated locally only and ignored by git
- `chr/bank_fixed.txt`: fixed PRG-bank hex dump, generated locally only and ignored by git
- `font/chr_bank_##_8x8.png`: CHR banks rendered as 8x8 tiles, generated locally only and ignored by git
- `font/chr_bank_##_8x16.png`: CHR banks rendered as 8x16 tile pairs, generated locally only and ignored by git
- `font/chr_bank_##_*_labeled.png`: labeled tile sheets, generated locally only and ignored by git

## Findings so far

- Plain Shift-JIS extraction does not produce normal dialogue. The hits are mostly false positives from binary data, so the game likely uses a custom tile/code mapping rather than raw Shift-JIS strings.
- `font/chr_bank_07_8x16.png` is the strongest font candidate. It visibly contains kana, numerals, Latin letters, and symbols.
- After rendering bank 07 as `8x8`, the font block is clearer than the `8x16` view. Hiragana begins around tile `0x101`; numerals begin around `0x1C0`; Latin capitals begin around `0x1E1`.
- CHR ROM starts at `ROM+0x20010`; the 8KB rendered CHR bank 07 used by the current font analysis covers `ROM+0x2E010-0x3000F`. The structured map records `あ=tile 0x101/ROM+0x2F020`, `ま=tile 0x120/ROM+0x2F210`, `ん=tile 0x12F/ROM+0x2F300`, digits `0x1C0-0x1C9`, and Latin capitals `0x1E1-0x1FA`.
- The current v0.1 patch inventory writes 181 8x8 slots, `tile 0x101-0x1B5` (`ROM+0x2F020-0x2FB6F`). All 181 slots changed in the generated patched ROM, with 2,433 changed bytes. Reference digit tiles `0x1C0-0x1C9` and uppercase Latin tiles `0x1E1-0x1FA` have `0` changed bytes, so the current Bank7 font patch does not overwrite those reference ranges.
- The current slot assignment is mechanical `char_map.json` order, so `tile 0x101` maps from original `あ` to patched `!`, then punctuation/digits/Latin before Hangul syllables. This is useful for reproducibility, but final text patching still needs an explicit character-to-PRG-byte allocation plan before translating strings.
- The compact Korean slot plan for the current Bank 1 inventory needs 18 Hangul syllables (`힘`, `카`, `타`, `나`, `다`, `리`, `헤`, `이`, `시`, `치`, `창`, `약`, `장`, `비`, `돈`, `라`, `프`, `츠`) out of 181 available Bank7 patch slots. This plan is not applied to the ROM yet; it defines the next explicit character allocation needed before PRG text bytes are rewritten.
- `scripts/build_patch_from_plan.py` applies that compact plan to CHR Bank 07 only and writes `output/kunio_period_drama_korean_plan_v0.2.nes`. The planned build changes 18 glyph slots / 252 bytes, all within `ROM+0x2F020-0x2F13E`, and writes a build report at `output/kunio_period_drama_korean_plan_v0.2_build_report.json`. It still does not rewrite PRG text bytes.
- `scripts/build_prg_patch_from_plan.py` builds the first conservative PRG+CHR experiment, `output/kunio_period_drama_korean_prg_plan_v0.3.nes`. It starts from the planned Bank7 font ROM and patches only equal-length `runtime-confirmed` PRG targets. The current run applies `ROM+0x07227` (`カタナ` -> `카타나`, `8A 94 99` -> `88 89 8A`) and deliberately skips `ROM+0x071A4` (`ちから` -> `힘`) because it would shrink 3 bytes to 1 byte and needs confirmed padding/control rules.
- `prg_padding_options.md` confirms direct equal-length replacements are safe candidates for the current `カタナ` -> `카타나` records, while `ちから` -> `힘` remains `needs-padding-rule` because it leaves non-fill tail bytes `88 AA`. Do not apply shortened replacements until FCEUX confirms the renderer's padding/terminator behavior for that record.
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

- The `ROM+0x05610-0x05810` watch range splits into 73 tentative `0xFF`-delimited blocks. The block map now records the original `plus-0x7A` decode, the best shifted-low decodes, and translation-data hits inside each block. Only `はし` at `ROM+0x0569D` exact-matches `translation_data.txt` under the current `plus-0x7A` model, but shifted-low matches identify several breakpoint-ready watch-range candidates: `たついち` at `ROM+0x0562F`, `へいしち` at `ROM+0x05643`, `カタナ` at `ROM+0x05644`, and additional `はし`-like hits at `0x0561A`, `0x056DA`, `0x0571C`, and `0x057D4`.
- `bank1_text_block_map.json` now preserves those 73 blocks in machine-readable form. It records 9 watch-range translation hits across 7 blocks, with 8 distinct equal-length patch candidates from `prg_padding_options.json`: `0x0561A`, `0x0562F`, `0x05643`, `0x05644`, `0x0569D`, `0x056DA`, `0x0571C`, and `0x057D4`. These are length-safe candidates, but still need runtime screen confirmation before being promoted beyond static/watch-range evidence.
- The broader translation-offset scan found 315 total candidates, including 119 in Bank 1 and 9 inside the `ROM+0x05610-0x05810` watch range. High-value Bank 1 candidates include `カタナ` at `ROM+0x05644`, `0x06295`, `0x0631C`, `0x0635A`, `0x07227`; `くすり` at `0x05BDF`; `ちから` at `0x06605`, `0x066FB`, `0x06845`, `0x06B4A`, `0x071A4`; `そうび` at `0x0602E`, `0x06BDF`, `0x06FA1`; `おかね` at `0x06DE3`; and `ライフ` at `0x0736A`, `0x0739D`.
- `bank1_offset_inventory.md` currently consolidates 43 offsets: 36 breakpoint targets plus supplemental watch-range hits. Runtime-confirmed offsets are `ROM+0x071A4` (`ちから`/힘, active expected-byte match in FCEUX read-watch) and `ROM+0x07227` (`カタナ`/카타나, preserved runtime evidence). Menu-category targets and full event dialogue blocks are not runtime-confirmed yet; the inventory keeps them marked as gaps instead of promoting static matches to final offsets.
- `bank1_candidate_contexts.md` narrows those hits into breakpoint-ready records. Useful first checks are `ROM+0x05644` / CPU `$9633` for the watch-range weapon label, `ROM+0x05BDF` / `$9BCD` for recovery text, `ROM+0x06DE3` / `$ADD1` for money UI, and `ROM+0x0736A` / `$B359` plus `ROM+0x0739D` / `$B38C` for life UI.
- A YouTube gameplay video can help transcribe dialogue and confirm scene order, but it does not replace ROM analysis because patching still needs exact ROM offsets, byte encodings, control codes, and active runtime banks.

## FCEUX Lua automation

The repository includes `lua/kunio_auto_dump.lua` and
`scripts/run_fceux_lua_analysis.py` to reduce manual GUI work. The launcher
stages FCEUX in an ASCII-only `%TEMP%` path, opens the ROM, runs the Lua script,
and mirrors generated dumps into `rom_analysis/fceux_lua/`.

Run:

```powershell
python scripts/run_fceux_lua_analysis.py --frames 10800 --timeout 240
```

To watch the current Bank 1 item/status/UI candidate records for CPU reads:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua --frames 10800 --timeout 240 --final-output rom_analysis/fceux_bank1_watch --no-dump-hex --no-dump-bin
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
- `lua/kunio_bank1_watch.lua` registers read callbacks for the current
  breakpoint-ready Bank 1 records. It now loads the generated
  `lua/kunio_bank1_targets.lua` file when present; the current generated list
  contains 36 item/menu/UI-style targets from `bank1_watch_targets.json`.
  A non-empty `bank1_reads.tsv` is evidence that the CPU address was read, and
  `active_expected_match=true` is stronger evidence that the expected candidate
  bytes were actually mapped at that CPU range during the read.
- A 900-frame validation run confirmed `memory.registerread` support in the
  local FCEUX build: 124 watched CPU addresses were registered and 247 read
  hits were captured. The run observed a strong context match for
  `ROM+0x071A4` (`ちから` candidate): all 11 hits had an active expected-byte
  match for `93 88 AA`. `ROM+0x06FA1` was also read frequently, but all 236
  hits had `active_expected_match=false`, so treat it as an address/bank-switch
  follow-up target rather than confirmed text.
- A PPU write watch run captured 88 useful frames and 19,926 nametable writes.
  The original analyzer found no exact target matches because it only grouped
  same-frame, +1-address write runs. `scripts/analyze_ppu_watch_v2.py`
  reconstructs each frame's final nametable, filters attribute-table writes plus
  `0x00`/`0x7A` fill tiles, and then scans address-ordered streams. That
  recovered five identity matches for the `ちから` byte sequence `93 88 AA`:
  `ROM+0x06605`, `0x066FB`, `0x06845`, `0x06B4A`, and `0x071A4`.
- The first v0.1 patch builder wrote the generated font outside CHR Bank 07
  because it treated Bank7's visually identified `0x101` tile as an 8x16 index
  and used `tile * 32`. `scripts/build_patch.py` now uses repo-local paths and
  writes one 16-byte 8x8 tile per Bank7 slot (`0x101-0x1B5`). The regenerated
  patched ROM differs from the base ROM only in `ROM+0x2F020-0x2FB6E`, which is
  inside the confirmed Bank7 range `ROM+0x2E010-0x3000F`. The build report is
  `output/kunio_period_drama_korean_v0.1_build_report.json`.

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
8. Confirm whether the candidate offsets in `translation_offset_candidates.md` and the breakpoint-ready records in `bank1_candidate_contexts.md` are read when their corresponding item/status/menu text appears.
9. Save the trace log, PPU screenshots, and any nametable/memory dumps into this `rom_analysis/` folder.

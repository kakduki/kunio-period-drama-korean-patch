# Manual Screen Capture Workflow

This workflow replaces long blind autoplay runs. Use it when a specific
dialogue/menu/status screen is visible in FCEUX and needs patch evidence.

## Why

The current Lua autoplay can reach repeatable menu/status transfer windows, but
it is not a reliable full gameplay bot. Running it for hours usually repeats
early/title/menu states and wastes time. For real translation work, a manually
reached screen is higher-value evidence.

## Capture Steps

1. Open the ROM in FCEUX.
2. Manually play to the Japanese text screen you want to analyze.
3. Pause on that exact screen.
4. In FCEUX, run `lua/kunio_manual_screen_dump.lua`.
5. The script writes a one-shot dump under `rom_analysis/manual_screen_dump/`.
6. Summarize the latest dump:

```powershell
python scripts/analyze_manual_screen_dump.py
```

## Patched v0.4 Verification

For the current equal-length patch experiment, open this ROM instead:

```text
output/kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes
```

Then manually reach a screen from `rom_analysis/manual_capture_queue.md` and run:

```text
lua/kunio_manual_v04_screen_dump.lua
```

This wrapper uses `lua/kunio_v04_equal_length_targets.lua`, so
`active_expected_match=true` means the patched Korean byte sequence is mapped in
CPU memory on that manually reached screen.

Summarize the latest v0.4 dump:

```powershell
python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v04 --output rom_analysis/manual_screen_dump_v04/summary.md
```

## Broad v0.5 Candidate Read-Watch

For future v0.5 candidates from `rom_analysis/broad_scan_patchability.md`,
use the base ROM first and manually reach the related screen. Then run a short
read-watch against original bytes:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_broad_scan_candidate_targets.lua --frames 900 --timeout 60 --final-output rom_analysis/fceux_broad_scan_candidates --clean-output --no-dump-hex --no-dump-bin
```

Only promote a broad candidate after the read hit and the visible screen both
match the intended label/dialogue. These targets do not create a v0.5 ROM.

## Output

Each capture writes files named like:

- `manual_frame_XXXXXX_meta.txt`
- `manual_frame_XXXXXX_cpu_ram.bin`
- `manual_frame_XXXXXX_cpu_ram.txt`
- `manual_frame_XXXXXX_sram_6000_7fff.bin`
- `manual_frame_XXXXXX_sram_6000_7fff.txt`
- `manual_frame_XXXXXX_screen.gd`
- `manual_frame_XXXXXX_target_records.tsv`

The summary script writes:

- `rom_analysis/manual_screen_dump/summary.md`

## Interpretation

- `active_expected_match=true` means the manually reached screen has one of the
  generated Bank 1 target byte sequences mapped in CPU memory at the expected
  range.
- No match does not mean the screen is useless. It means the current Bank 1
  target list does not cover it yet, so the captured RAM/screenshot should feed
  broader static matching.
- The `.gd` file is raw FCEUX/GD screenshot data from `gui.gdscreenshot()`.

## Cutoff Rule

Do not keep a blind autoplay run alive if the visible FCEUX window is stuck on
the opening/title/first menu screen. Stop it and switch to manual capture.

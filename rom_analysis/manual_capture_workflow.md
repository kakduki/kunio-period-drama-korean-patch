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

## Capture Watcher

For longer manual play, run this once instead of reopening Lua for every screen:

```text
lua/kunio_manual_capture_watch.lua
```

While the watcher is running:

- Press `D` on a useful text/menu/status screen to save a dump.
- Press `Q` to stop the watcher.
- The watcher does not autoplay or advance dialogue for you.

## Patched v0.4.2 Verification

For the current font-expanded patch experiment, open this ROM instead:

```text
output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes
```

Then manually reach a screen from `rom_analysis/manual_capture_queue.md` and run:

```text
lua/kunio_manual_v042_screen_dump.lua
```

For multiple v0.4.2 screens in one play session, run:

```text
lua/kunio_manual_v042_capture_watch.lua
```

This wrapper reuses `lua/kunio_v041_conflict_safe_targets.lua`, so
`active_expected_match=true` means the patched Korean byte sequence is mapped in
CPU memory on that manually reached screen.

Summarize the latest v0.4.2 dump:

```powershell
python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v042 --output rom_analysis/manual_screen_dump_v042/summary.md
```

## Broad v0.5 Candidate Read-Watch

For future v0.5 candidates from `rom_analysis/broad_scan_patchability.md`,
use the base ROM first and manually reach the related screen. Then run the
manual wrapper:

```text
lua/kunio_manual_broad_scan_dump.lua
```

For multiple broad-scan screens in one play session, run:

```text
lua/kunio_manual_broad_scan_capture_watch.lua
```

Summarize the latest broad-scan dump:

```powershell
python scripts/analyze_broad_scan_manual_dump.py
```

For a short read-watch run instead of a one-shot dump, use:

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

# Full Korean Candidate Short Progression Probe

Status: **PASS_GAMEPLAY_ENTRY**

## Run

- Candidate ROM: `output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes`
- Candidate MD5: `d062b19d23050cd4e148e22fbfff57b7`
- Script: `lua/kunio_stage_progression_probe.lua`
- Frame cap: `2,400`
- Terminal reason: `lua_done`
- Launcher result: `PASS` (exit code 0)

Command:

```text
python scripts/run_fceux_lua_analysis.py --rom output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes --lua-script lua/kunio_stage_progression_probe.lua --frames 2400 --timeout 120 --final-output rom_analysis/stage_progression_probe_full_korean_candidate_short --clean-output --no-dump-hex --no-dump-bin --lua-env KUNIO_EXTRA_DIALOGUE_START=1 --lua-env KUNIO_COMBAT_SWEEP=1
```

## Checkpoints

| frame | evidence | result |
| ---: | --- | --- |
| 120-302 | title/menu route changes | PASS |
| 392 | first dialogue screen | PASS |
| 667 | extra `Start` advances dialogue | PASS |
| 757 | field screen and normal mapper state | PASS |
| 915 | combat screen begins | PASS |
| 1,049-1,319 | distinct combat screen fingerprints | PASS |
| 2,400 | finite script completion | PASS |

## Interpretation

The candidate does not remain on the opening screen when run with the bounded
stage route. The earlier long explorer run was misleading because it chained
menu cycles after entry and its launcher missed the final completion row at
timeout; the captured output still contained `7200\tdone` and 17 unique screen
fingerprints. The short route now observes and accepts `lua_done` directly.

## Limits

- This proves boot, dialogue transition, field recovery, and combat entry only.
- It does not prove every boss encounter, boss defeat, or all 244 pointer rows.
- Native FCEUX GD screenshots are retained as evidence, but release visual
  approval still requires decoded screen comparisons for high-risk contexts.
- The candidate remains a development build; release verdict is `UNKNOWN`.

Evidence directory: `rom_analysis/stage_progression_probe_full_korean_candidate_short`.

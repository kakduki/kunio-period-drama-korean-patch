# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_v042_primary_watch_short`

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --rom output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_v041_conflict_safe_targets.lua --frames 1800 --timeout 60 --final-output rom_analysis/fceux_v042_primary_watch_short --clean-output --no-dump-hex --no-dump-bin --hit-limit 5000
```

## Run result

- Final frame: `1800`
- Final reason: `lua_done`
- Registered watched CPU addresses: `148`
- Total read hits: `0`
- Callback detail: `callback_mode=true;target_source=kunio_v041_conflict_safe_targets.lua;targets=10`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | active expected matches | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| _none_ |  |  |  | 0 |  |  |  | 0 |  |  |

## Readable Labels

| label | expected text | Korean | screen hint |
| --- | --- | --- | --- |

## Details

| label | top CPU addresses | top values | expected bytes | top byte diff | record snapshot evidence |
| --- | --- | --- | --- | --- | --- |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- `active expected matches` counts hits where the watched CPU record currently contained the expected byte sequence.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.

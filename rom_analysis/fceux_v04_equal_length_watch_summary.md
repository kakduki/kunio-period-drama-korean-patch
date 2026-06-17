# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_v04_equal_length_watch`

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --rom output/kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_v04_equal_length_targets.lua --frames 3600 --timeout 120 --final-output rom_analysis/fceux_v04_equal_length_watch --clean-output --no-dump-hex --no-dump-bin
```

## Run result

- Final frame: `3600`
- Final reason: `lua_done`
- Registered watched CPU addresses: `181`
- Total read hits: `5`
- Callback detail: `callback_mode=true;target_source=kunio_v04_equal_length_targets.lua;targets=13`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | active expected matches | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `v04_rom_07227_candidate_84` | 무기 | `ROM+0x07227` | `$B216-$B21A` | 5 | 1975 | 1983 | 5 | 5 | yes | `AF 00 85 88 89 8A 00 82` |

## Details

| label | top CPU addresses | top values | expected bytes | top byte diff | record snapshot evidence |
| --- | --- | --- | --- | --- | --- |
| `v04_rom_07227_candidate_84` | `$B216`:1, `$B217`:1, `$B218`:1, `$B219`:1 | `85`:1, `88`:1, `89`:1, `8A`:1 | `88 89 8A` | `` | `yes: 85 88 89 8A 00` |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- `active expected matches` counts hits where the watched CPU record currently contained the expected byte sequence.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.

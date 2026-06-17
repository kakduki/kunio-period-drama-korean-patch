# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_v04_equal_length_watch_long`

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --rom output/kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_v04_equal_length_targets.lua --frames 10800 --timeout 240 --final-output rom_analysis/fceux_v04_equal_length_watch_long --clean-output --no-dump-hex --no-dump-bin
```

## Run result

- Final frame: `6747`
- Final reason: `hit_limit`
- Registered watched CPU addresses: `181`
- Total read hits: `50000`
- Callback detail: `callback_mode=true;target_source=kunio_v04_equal_length_targets.lua;targets=13`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | active expected matches | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `v04_rom_0736a_candidate_93` | UI | `ROM+0x0736A` | `$B359-$B35E` | 49995 | 5478 | 6747 | 6 | 0 | no | `60 AD A2 7A 29 10 F0 1C` |
| `v04_rom_07227_candidate_84` | 무기 | `ROM+0x07227` | `$B216-$B21A` | 5 | 1975 | 1983 | 5 | 5 | yes | `AF 00 85 88 89 8A 00 82` |

## Details

| label | top CPU addresses | top values | expected bytes | top byte diff | record snapshot evidence |
| --- | --- | --- | --- | --- | --- |
| `v04_rom_0736a_candidate_93` | `$B35B`:15659, `$B35C`:15659, `$B35D`:15659, `$B359`:1207 | `00`:15658, `6C`:15055, `2E`:15055, `A2`:604 | `96 8E 97` | `` | `no: A2 7A 29 10 F0 1C` |
| `v04_rom_07227_candidate_84` | `$B216`:1, `$B217`:1, `$B218`:1, `$B219`:1 | `85`:1, `88`:1, `89`:1, `8A`:1 | `88 89 8A` | `` | `yes: 85 88 89 8A 00` |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- `active expected matches` counts hits where the watched CPU record currently contained the expected byte sequence.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.

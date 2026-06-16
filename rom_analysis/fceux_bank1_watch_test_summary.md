# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_bank1_watch_test`

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua --frames 900 --timeout 90 --final-output rom_analysis/fceux_bank1_watch_test --clean-output --no-dump-hex --no-dump-bin
```

## Run result

- Final frame: `900`
- Final reason: `lua_done`
- Registered watched CPU addresses: `334`
- Total read hits: `677`
- Callback detail: `callback_mode=true;target_source=generated;targets=36`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | active expected matches | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `rom_05bba_candidate_7a` | 무기 | `ROM+0x05BBA` | `$9BA5-$9BAD` | 430 | 149 | 254 | 6 | 0 | no | `01 01 01 01 40 40 40 40` |
| `rom_06fa1_candidate_8d` | UI | `ROM+0x06FA1` | `$AF91-$AF9A` | 236 | 604 | 802 | 10 | 0 | no | `7F 43 CA 02 C4 46 C5 FF` |
| `rom_071a4_candidate_82` | 능력치 | `ROM+0x071A4` | `$B192-$B19C` | 11 | 358 | 376 | 11 | 11 | yes | `82 00 9F B4 93 88 AA A6` |

## Details

| label | top CPU addresses | top values | expected bytes | record snapshot evidence |
| --- | --- | --- | --- | --- |
| `rom_05bba_candidate_7a` | `$9BA9`:77, `$9BAA`:77, `$9BA5`:69, `$9BA6`:69 | `01`:430 | `9F A3` | `no: 01 01 01 01 01 01 40 40 40` |
| `rom_06fa1_candidate_8d` | `$AF95`:46, `$AF96`:46, `$AF97`:46, `$AF98`:44 | `C5`:46, `FF`:46, `01`:46, `CE`:44 | `9C 90 A8` | `no: CA 02 C4 46 C5 FF 01 CE 3C 95` |
| `rom_071a4_candidate_82` | `$B192`:1, `$B193`:1, `$B194`:1, `$B195`:1 | `9F`:1, `B4`:1, `93`:1, `88`:1 | `93 88 AA` | `yes: 9F B4 93 88 AA A6 83 CA F8 F9 00` |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- `active expected matches` counts hits where the watched CPU record currently contained the expected byte sequence.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.

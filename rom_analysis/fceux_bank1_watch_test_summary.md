# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_bank1_watch_test`

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua --frames 900 --timeout 90 --final-output rom_analysis/fceux_bank1_watch_test --clean-output --no-dump-hex --no-dump-bin
```

## Run result

- Final frame: `900`
- Final reason: `lua_done`
- Registered watched CPU addresses: `124`
- Total read hits: `247`
- Callback detail: `callback_mode=true`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `soubi_ui_c` | ui | `ROM+0x06FA1` | `$AF91-$AF9A` | 236 | 604 | 802 | 10 | no | `7F 43 CA 02 C4 46 C5 FF` |
| `chikara_stat_e` | stat | `ROM+0x071A4` | `$B192-$B19C` | 11 | 358 | 376 | 11 | yes | `82 00 9F B4 93 88 AA A6` |

## Details

| label | top CPU addresses | top values | expected bytes |
| --- | --- | --- | --- |
| `soubi_ui_c` | `$AF95`:46, `$AF96`:46, `$AF97`:46, `$AF98`:44 | `C5`:46, `FF`:46, `01`:46, `CE`:44 | `9C 90 A8` |
| `chikara_stat_e` | `$B192`:1, `$B193`:1, `$B194`:1, `$B195`:1 | `9F`:1, `B4`:1, `93`:1, `88`:1 | `93 88 AA` |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.

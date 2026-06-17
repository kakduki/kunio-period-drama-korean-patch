# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_padding_exp_pad_ff_watch`

Command:

```powershell
python scripts\run_fceux_lua_analysis.py --rom output\kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_ff.nes --lua-script lua\kunio_bank1_watch.lua --target-lua lua\kunio_padding_exp_pad_ff_targets.lua --frames 3600 --timeout 120 --final-output rom_analysis\fceux_padding_exp_pad_ff_watch --clean-output --no-dump-hex --no-dump-bin
```

## Run result

- Final frame: `3600`
- Final reason: `lua_done`
- Registered watched CPU addresses: `11`
- Total read hits: `4`
- Callback detail: `callback_mode=true;target_source=kunio_padding_exp_pad_ff_targets.lua;targets=1`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | active expected matches | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `padding_pad_ff_rom_071a4_candidate_82` | 능력치 | `ROM+0x071A4` | `$B192-$B19C` | 4 | 358 | 364 | 4 | 4 | yes | `82 00 9F B4 87 FF FF A6` |

## Details

| label | top CPU addresses | top values | expected bytes | top byte diff | record snapshot evidence |
| --- | --- | --- | --- | --- | --- |
| `padding_pad_ff_rom_071a4_candidate_82` | `$B192`:1, `$B193`:1, `$B194`:1, `$B195`:1 | `9F`:1, `B4`:1, `87`:1, `FF`:1 | `87 FF FF` | `` | `yes: 9F B4 87 FF FF A6 83 CA F8 F9 00` |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- `active expected matches` counts hits where the watched CPU record currently contained the expected byte sequence.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.

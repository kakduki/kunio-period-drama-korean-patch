# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_broad_scan_watch_short`

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_broad_scan_candidate_targets.lua --frames 1800 --timeout 60 --final-output rom_analysis/fceux_broad_scan_watch_short --clean-output --no-dump-hex --no-dump-bin --hit-limit 5000
```

## Run result

- Final frame: `1327`
- Final reason: `hit_limit`
- Registered watched CPU addresses: `24`
- Total read hits: `5000`
- Callback detail: `callback_mode=true;target_source=kunio_broad_scan_candidate_targets.lua;targets=7`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | active expected matches | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `broad_0440c_kajiya` | 스테이지 | `ROM+0x0440C` | `$83FC-$83FE` | 3449 | 1030 | 1327 | 3 | 0 | no | `09 49 FF 18 69 01 4C 05` |
| `broad_048f4_tatsuji` | 보스 | `ROM+0x048F4` | `$88E4-$88E6` | 1311 | 324 | 1327 | 3 | 0 | no | `A5 00 20 F7 88 C8 B9 C1` |
| `broad_05be5_tatsuji` | 보스 | `ROM+0x05BE5` | `$9BD5-$9BD7` | 240 | 1051 | 1323 | 3 | 0 | no | `03 03 03 00 00 00 00 00` |

## Readable Labels

| label | expected text | Korean | screen hint |
| --- | --- | --- | --- |
| `broad_0440c_kajiya` | かじや | 대장간 | look for a blacksmith/shop or blacksmith-stage label |
| `broad_048f4_tatsuji` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context |
| `broad_05be5_tatsuji` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context |

## Details

| label | top CPU addresses | top values | expected bytes | top byte diff | record snapshot evidence |
| --- | --- | --- | --- | --- | --- |
| `broad_0440c_kajiya` | `$83FC`:1150, `$83FD`:1150, `$83FE`:1149 | `FF`:1150, `18`:1150, `69`:1149 | `CA D0 E9` | `` | `no: FF 18 69` |
| `broad_048f4_tatsuji` | `$88E4`:437, `$88E5`:437, `$88E6`:437 | `20`:437, `F7`:437, `88`:437 | `07 09 03` | `` | `no: 20 F7 88` |
| `broad_05be5_tatsuji` | `$9BD5`:80, `$9BD6`:80, `$9BD7`:80 | `00`:160, `03`:80 | `97 99 93` | `` | `no: 03 00 00` |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- `active expected matches` counts hits where the watched CPU record currently contained the expected byte sequence.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.

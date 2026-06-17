# v0.4 Equal-Length FCEUX Targets

These targets watch for patched PRG bytes from the v0.4 equal-length static experiment.

- Source report: `output\kunio_period_drama_korean_prg_plan_v0.4_equal_length_static_build_report.json`
- Patched MD5: `e50d9c974d9968170f932a7ed51fe52e`
- Targets: `13`
- Missing inventory rows: `0`

Run with:

```powershell
python scripts/run_fceux_lua_analysis.py --rom output/kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_v04_equal_length_targets.lua --frames 10800 --timeout 240 --final-output rom_analysis/fceux_v04_equal_length_watch --clean-output --no-dump-hex --no-dump-bin
```

## Targets

| ROM hit | CPU range | Japanese | Korean | category | evidence | old bytes | patched bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `0x0561A` | `$95BE-$960F` | はし | 다리 | 스테이지 | static-candidate+pointer | `96 88` | `8B 8C` |
| `0x0562F` | `$961A-$9623` | たついち | 타츠이치 | 보스 | static-candidate | `90 92 82 91` | `89 98 8E 90` |
| `0x05643` | `$9633-$9637` | へいしち | 헤이시치 | 보스 | static-candidate+pointer | `9D 82 8C 91` | `8D 8E 8F 90` |
| `0x0569D` | `$968C-$968F` | はし | 다리 | 스테이지 | encoding-exact | `A0 92` | `8B 8C` |
| `0x056DA` | `$96C5-$96CE` | はし | 다리 | 스테이지 | static-candidate | `9A 8C` | `8B 8C` |
| `0x0571C` | `$9706-$9714` | はし | 다리 | 스테이지 | static-candidate | `92 84` | `8B 8C` |
| `0x057D4` | `$97C4-$97C8` | はし | 다리 | 스테이지 | static-candidate+pointer | `A6 98` | `8B 8C` |
| `0x06295` | `$A284-$A28E` | カタナ | 카타나 | 무기 | static-candidate+pointer | `82 8C 91` | `88 89 8A` |
| `0x0631C` | `$A309-$A314` | カタナ | 카타나 | 무기 | static-candidate+pointer | `82 8C 91` | `88 89 8A` |
| `0x0635A` | `$A349-$A352` | カタナ | 카타나 | 무기 | static-candidate | `82 8C 91` | `88 89 8A` |
| `0x07227` | `$B216-$B21A` | カタナ | 카타나 | 무기 | runtime-confirmed | `8A 94 99` | `88 89 8A` |
| `0x0736A` | `$B359-$B35E` | ライフ | 라이프 | UI | static-candidate+pointer | `BB 95 AF` | `96 8E 97` |
| `0x0739D` | `$B38C-$B391` | ライフ | 라이프 | UI | static-candidate+pointer | `BB 95 AF` | `96 8E 97` |

## Notes

- A hit with `active_expected_match=true` means the patched byte sequence is active in the watched CPU record.
- Static/watch-range targets still need screen-state confirmation before being promoted to final patch offsets.
- The overlapping `ROM+0x05644` candidate is not present here because the v0.4 builder skipped it in favor of `ROM+0x05643`.

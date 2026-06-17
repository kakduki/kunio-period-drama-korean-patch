# PRG Padding Options

This report compares original candidate byte spans with planned Korean PRG bytes.

Risk labels:

- `safe-equal-length`: direct byte replacement can preserve record length.
- `maybe-pad-over-fill`: planned bytes are shorter, but the remaining bytes are known fill/control candidates.
- `needs-padding-rule`: planned bytes are shorter and the remaining original bytes are not known safe fill bytes.
- `unsafe-overflow`: planned bytes are longer than the candidate span.

## Summary

| risk | count |
| --- | ---: |
| needs-padding-rule | 29 |
| safe-equal-length | 14 |

## needs-padding-rule

| evidence | ROM hit | category | Japanese | Korean | len old/new | old bytes | planned bytes | tail | reason |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| runtime-confirmed | `0x071A4` | 능력치 | ちから | 힘 | 3/1 | `93 88 AA` | `87` | `88 AA` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x058FB` | 무기 | やり | 창 | 2/1 | `9E A2` | `91` | `A2` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x06001` | 무기 | やり | 창 | 2/1 | `A3 A7` | `91` | `A7` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x06479` | 무기 | やり | 창 | 2/1 | `A4 A8` | `91` | `A8` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x065B0` | 무기 | やり | 창 | 2/1 | `A5 A9` | `91` | `A9` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x06605` | 능력치 | ちから | 힘 | 3/1 | `93 88 AA` | `87` | `88 AA` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x06A3D` | 무기 | やり | 창 | 2/1 | `9E A2` | `91` | `A2` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x06A66` | 무기 | やり | 창 | 2/1 | `9E A2` | `91` | `A2` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x06B4A` | 능력치 | ちから | 힘 | 3/1 | `93 88 AA` | `87` | `88 AA` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x06FDE` | 무기 | やり | 창 | 2/1 | `A5 A9` | `91` | `A9` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate | `0x0704F` | 무기 | やり | 창 | 2/1 | `9F A3` | `91` | `A3` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x05AA3` | 무기 | やり | 창 | 2/1 | `9C A0` | `91` | `A0` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x05AA5` | 무기 | やり | 창 | 2/1 | `9C A0` | `91` | `A0` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x05BBA` | 무기 | やり | 창 | 2/1 | `9F A3` | `91` | `A3` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x05BDF` | 회복 | くすり | 약 | 3/1 | `82 87 A3` | `92` | `87 A3` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x05C09` | 무기 | やり | 창 | 2/1 | `9F A3` | `91` | `A3` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x05C69` | 무기 | やり | 창 | 2/1 | `9F A3` | `91` | `A3` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x0602E` | UI | そうび | 장비 | 3/2 | `9C 90 A8` | `93 94` | `A8` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x066FB` | 능력치 | ちから | 힘 | 3/1 | `93 88 AA` | `87` | `88 AA` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x06839` | 무기 | やり | 창 | 2/1 | `A3 A7` | `91` | `A7` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x06845` | 능력치 | ちから | 힘 | 3/1 | `93 88 AA` | `87` | `88 AA` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x068C3` | 무기 | やり | 창 | 2/1 | `96 9A` | `91` | `9A` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x0691E` | 무기 | やり | 창 | 2/1 | `A5 A9` | `91` | `A9` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x069C5` | 무기 | やり | 창 | 2/1 | `9E A2` | `91` | `A2` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x06BC6` | 무기 | やり | 창 | 2/1 | `A0 A4` | `91` | `A4` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x06BDF` | UI | そうび | 장비 | 3/2 | `9C 90 A8` | `93 94` | `A8` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x06D1B` | 무기 | やり | 창 | 2/1 | `A5 A9` | `91` | `A9` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x06DE3` | UI | おかね | 돈 | 3/1 | `85 86 98` | `95` | `86 98` | remaining original bytes decode as non-fill candidate text/control bytes |
| static-candidate+pointer | `0x06FA1` | UI | そうび | 장비 | 3/2 | `9C 90 A8` | `93 94` | `A8` | remaining original bytes decode as non-fill candidate text/control bytes |

## safe-equal-length

| evidence | ROM hit | category | Japanese | Korean | len old/new | old bytes | planned bytes | tail | reason |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| encoding-exact | `0x0569D` | 스테이지 | はし | 다리 | 2/2 | `A0 92` | `8B 8C` | `-` | planned bytes exactly fill candidate span |
| runtime-confirmed | `0x07227` | 무기 | カタナ | 카타나 | 3/3 | `8A 94 99` | `88 89 8A` | `-` | planned bytes exactly fill candidate span |
| static-candidate | `0x0562F` | 보스 | たついち | 타츠이치 | 4/4 | `90 92 82 91` | `89 98 8E 90` | `-` | planned bytes exactly fill candidate span |
| static-candidate | `0x056DA` | 스테이지 | はし | 다리 | 2/2 | `9A 8C` | `8B 8C` | `-` | planned bytes exactly fill candidate span |
| static-candidate | `0x0571C` | 스테이지 | はし | 다리 | 2/2 | `92 84` | `8B 8C` | `-` | planned bytes exactly fill candidate span |
| static-candidate | `0x0635A` | 무기 | カタナ | 카타나 | 3/3 | `82 8C 91` | `88 89 8A` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x0561A` | 스테이지 | はし | 다리 | 2/2 | `96 88` | `8B 8C` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x05643` | 보스 | へいしち | 헤이시치 | 4/4 | `9D 82 8C 91` | `8D 8E 8F 90` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x05644` | 무기 | カタナ | 카타나 | 3/3 | `82 8C 91` | `88 89 8A` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x057D4` | 스테이지 | はし | 다리 | 2/2 | `A6 98` | `8B 8C` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x06295` | 무기 | カタナ | 카타나 | 3/3 | `82 8C 91` | `88 89 8A` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x0631C` | 무기 | カタナ | 카타나 | 3/3 | `82 8C 91` | `88 89 8A` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x0736A` | UI | ライフ | 라이프 | 3/3 | `BB 95 AF` | `96 8E 97` | `-` | planned bytes exactly fill candidate span |
| static-candidate+pointer | `0x0739D` | UI | ライフ | 라이프 | 3/3 | `BB 95 AF` | `96 8E 97` | `-` | planned bytes exactly fill candidate span |

## Notes

- `ちから` -> `힘` is deliberately left in `needs-padding-rule`: its remaining bytes are `88 AA`, not known fill/control bytes.
- Do not apply shorter replacements until the renderer's pad/terminator behavior is observed in FCEUX for the specific record.

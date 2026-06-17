# Korean Slot Allocation Plan

This is a planning artifact for assigning Korean glyphs to CHR Bank 07 patch slots before PRG text bytes are rewritten.

- Source inventory: `rom_analysis\bank1_offset_inventory.json`
- Patch tile range: `0x101-0x1B5`
- Available slots: **181**
- Required Korean glyphs for current inventory: **18**
- `current char_map tile` is `-` when the glyph exists only beyond the current 181-slot v0.1 patch range or is absent from `font/char_map.json`.

## Required Glyph Slots

| # | glyph | tile | ROM offset | planned PRG byte (+0x7A) | current char_map tile | used by count |
| ---: | --- | --- | --- | --- | --- | ---: |
| 0 | 힘 | `0x101` | `0x2F020` | `0x87` | `-` | 5 |
| 1 | 카 | `0x102` | `0x2F030` | `0x88` | `-` | 5 |
| 2 | 타 | `0x103` | `0x2F040` | `0x89` | `-` | 6 |
| 3 | 나 | `0x104` | `0x2F050` | `0x8A` | `-` | 5 |
| 4 | 다 | `0x105` | `0x2F060` | `0x8B` | `0x166` | 5 |
| 5 | 리 | `0x106` | `0x2F070` | `0x8C` | `0x180` | 5 |
| 6 | 헤 | `0x107` | `0x2F080` | `0x8D` | `-` | 1 |
| 7 | 이 | `0x108` | `0x2F090` | `0x8E` | `-` | 4 |
| 8 | 시 | `0x109` | `0x2F0A0` | `0x8F` | `0x1B5` | 1 |
| 9 | 치 | `0x10A` | `0x2F0B0` | `0x90` | `-` | 2 |
| 10 | 창 | `0x10B` | `0x2F0C0` | `0x91` | `-` | 19 |
| 11 | 약 | `0x10C` | `0x2F0D0` | `0x92` | `-` | 1 |
| 12 | 장 | `0x10D` | `0x2F0E0` | `0x93` | `-` | 3 |
| 13 | 비 | `0x10E` | `0x2F0F0` | `0x94` | `0x19F` | 3 |
| 14 | 돈 | `0x10F` | `0x2F100` | `0x95` | `0x16B` | 1 |
| 15 | 라 | `0x110` | `0x2F110` | `0x96` | `0x174` | 2 |
| 16 | 프 | `0x111` | `0x2F120` | `0x97` | `-` | 2 |
| 17 | 츠 | `0x112` | `0x2F130` | `0x98` | `-` | 1 |

## Target Encoding Preview

| evidence | ROM hit | category | Japanese | Korean | glyphs | planned PRG bytes | original candidate bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| runtime-confirmed | `0x071A4` | 능력치 | ちから | 힘 | 힘 | `0x87` | `93 88 AA` |
| runtime-confirmed | `0x07227` | 무기 | カタナ | 카타나 | 카타나 | `0x88 0x89 0x8A` | `8A 94 99` |
| encoding-exact | `0x0569D` | 스테이지 | はし | 다리 | 다리 | `0x8B 0x8C` | `A0 92` |
| static-candidate+pointer | `0x0561A` | 스테이지 | はし | 다리 | 다리 | `0x8B 0x8C` | `96 88` |
| static-candidate+pointer | `0x05643` | 보스 | へいしち | 헤이시치 | 헤이시치 | `0x8D 0x8E 0x8F 0x90` | `9D 82 8C 91` |
| static-candidate+pointer | `0x05644` | 무기 | カタナ | 카타나 | 카타나 | `0x88 0x89 0x8A` | `82 8C 91` |
| static-candidate+pointer | `0x057D4` | 스테이지 | はし | 다리 | 다리 | `0x8B 0x8C` | `A6 98` |
| static-candidate+pointer | `0x05AA3` | 무기 | やり | 창 | 창 | `0x91` | `9C A0` |
| static-candidate+pointer | `0x05AA5` | 무기 | やり | 창 | 창 | `0x91` | `9C A0` |
| static-candidate+pointer | `0x05BBA` | 무기 | やり | 창 | 창 | `0x91` | `9F A3` |
| static-candidate+pointer | `0x05BDF` | 회복 | くすり | 약 | 약 | `0x92` | `82 87 A3` |
| static-candidate+pointer | `0x05C09` | 무기 | やり | 창 | 창 | `0x91` | `9F A3` |
| static-candidate+pointer | `0x05C69` | 무기 | やり | 창 | 창 | `0x91` | `9F A3` |
| static-candidate+pointer | `0x0602E` | UI | そうび | 장비 | 장비 | `0x93 0x94` | `9C 90 A8` |
| static-candidate+pointer | `0x06295` | 무기 | カタナ | 카타나 | 카타나 | `0x88 0x89 0x8A` | `82 8C 91` |
| static-candidate+pointer | `0x0631C` | 무기 | カタナ | 카타나 | 카타나 | `0x88 0x89 0x8A` | `82 8C 91` |
| static-candidate+pointer | `0x066FB` | 능력치 | ちから | 힘 | 힘 | `0x87` | `93 88 AA` |
| static-candidate+pointer | `0x06839` | 무기 | やり | 창 | 창 | `0x91` | `A3 A7` |
| static-candidate+pointer | `0x06845` | 능력치 | ちから | 힘 | 힘 | `0x87` | `93 88 AA` |
| static-candidate+pointer | `0x068C3` | 무기 | やり | 창 | 창 | `0x91` | `96 9A` |
| static-candidate+pointer | `0x0691E` | 무기 | やり | 창 | 창 | `0x91` | `A5 A9` |
| static-candidate+pointer | `0x069C5` | 무기 | やり | 창 | 창 | `0x91` | `9E A2` |
| static-candidate+pointer | `0x06BC6` | 무기 | やり | 창 | 창 | `0x91` | `A0 A4` |
| static-candidate+pointer | `0x06BDF` | UI | そうび | 장비 | 장비 | `0x93 0x94` | `9C 90 A8` |
| static-candidate+pointer | `0x06D1B` | 무기 | やり | 창 | 창 | `0x91` | `A5 A9` |
| static-candidate+pointer | `0x06DE3` | UI | おかね | 돈 | 돈 | `0x95` | `85 86 98` |
| static-candidate+pointer | `0x06FA1` | UI | そうび | 장비 | 장비 | `0x93 0x94` | `9C 90 A8` |
| static-candidate+pointer | `0x0736A` | UI | ライフ | 라이프 | 라이프 | `0x96 0x8E 0x97` | `BB 95 AF` |
| static-candidate+pointer | `0x0739D` | UI | ライフ | 라이프 | 라이프 | `0x96 0x8E 0x97` | `BB 95 AF` |
| static-candidate | `0x0562F` | 보스 | たついち | 타츠이치 | 타츠이치 | `0x89 0x98 0x8E 0x90` | `90 92 82 91` |
| static-candidate | `0x056DA` | 스테이지 | はし | 다리 | 다리 | `0x8B 0x8C` | `9A 8C` |
| static-candidate | `0x0571C` | 스테이지 | はし | 다리 | 다리 | `0x8B 0x8C` | `92 84` |
| static-candidate | `0x058FB` | 무기 | やり | 창 | 창 | `0x91` | `9E A2` |
| static-candidate | `0x06001` | 무기 | やり | 창 | 창 | `0x91` | `A3 A7` |
| static-candidate | `0x0635A` | 무기 | カタナ | 카타나 | 카타나 | `0x88 0x89 0x8A` | `82 8C 91` |
| static-candidate | `0x06479` | 무기 | やり | 창 | 창 | `0x91` | `A4 A8` |
| static-candidate | `0x065B0` | 무기 | やり | 창 | 창 | `0x91` | `A5 A9` |
| static-candidate | `0x06605` | 능력치 | ちから | 힘 | 힘 | `0x87` | `93 88 AA` |
| static-candidate | `0x06A3D` | 무기 | やり | 창 | 창 | `0x91` | `9E A2` |
| static-candidate | `0x06A66` | 무기 | やり | 창 | 창 | `0x91` | `9E A2` |
| static-candidate | `0x06B4A` | 능력치 | ちから | 힘 | 힘 | `0x87` | `93 88 AA` |
| static-candidate | `0x06FDE` | 무기 | やり | 창 | 창 | `0x91` | `A5 A9` |
| static-candidate | `0x0704F` | 무기 | やり | 창 | 창 | `0x91` | `9F A3` |

## Notes

- This does not patch PRG text yet. It defines a compact Korean glyph slot plan for the currently known Bank 1 targets.
- Planned PRG bytes assume the same `CHR tile = PRG byte + 0x7A` renderer path. Shifted-low tables still need runtime confirmation before direct PRG replacement.
- Current `char_map.json` places punctuation/digits/Latin before Hangul, so many required Korean glyphs currently live at later slots than this compact plan.

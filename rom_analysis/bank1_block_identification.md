# Bank 1 Block Identification

This report merges the tentative `0xFF` block map for `ROM+0x05610-0x05810` with Bank 1 offset inventory, v0.4 patch status, and v0.4 PPU write-watch evidence.

## Summary

- Blocks analyzed: **73**
- Blocks with translation/inventory targets: **7**
- Blocks without targets: **66**
- Blocks with runtime active-byte evidence inside this range: **0**
- Blocks with v0.4 patched-byte PPU sequence evidence: **5**

Role counts:

- `event/dialogue-related`: 6
- `mixed: event/dialogue-related + items/equipment`: 1
- `unidentified`: 66

## Identified Blocks

| block | ROM range | bytes | identification | evidence | targets | v0.4/PPU status |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `0x05610-0x0561F` | 15 | event/dialogue-related | static-candidate+pointer+ppu-sequence | `0x0561A` event/dialogue-related はし (Hashi) `96 88` | applied, PPU ambiguous |
| 2 | `0x05620-0x05629` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 3 | `0x0562A-0x05633` | 9 | event/dialogue-related | static-candidate | `0x0562F` event/dialogue-related たついち (Tatsuichi) `90 92 82 91` | applied |
| 4 | `0x05634-0x05637` | 3 | unidentified | no translation-data target in this block yet | - | - |
| 5 | `0x05639-0x0563D` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 6 | `0x0563E-0x05642` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 7 | `0x05643-0x05647` | 4 | mixed: event/dialogue-related + items/equipment | static-candidate+pointer | `0x05643` event/dialogue-related へいしち (Heishichi) `9D 82 8C 91`<br>`0x05644` items/equipment カタナ (Katana) `82 8C 91` | applied<br>skipped, skip: overlaps already-applied target watch_rom_05643_보스_80 at 0x05643 |
| 8 | `0x05648-0x0564C` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 9 | `0x0564D-0x05651` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 10 | `0x05652-0x05656` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 11 | `0x05657-0x0565B` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 12 | `0x0565C-0x05660` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 13 | `0x05661-0x05665` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 14 | `0x05666-0x0566A` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 15 | `0x0566B-0x05674` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 16 | `0x05675-0x05679` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 17 | `0x0567A-0x0568C` | 18 | unidentified | no translation-data target in this block yet | - | - |
| 18 | `0x0568D-0x05691` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 19 | `0x05692-0x05696` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 20 | `0x05697-0x0569A` | 3 | unidentified | no translation-data target in this block yet | - | - |
| 21 | `0x0569C-0x0569F` | 3 | event/dialogue-related | encoding-exact+ppu-sequence | `0x0569D` event/dialogue-related はし (Hashi) `A0 92` | applied, PPU ambiguous |
| 22 | `0x056A1-0x056A4` | 3 | unidentified | no translation-data target in this block yet | - | - |
| 23 | `0x056A6-0x056AF` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 24 | `0x056B0-0x056C5` | 21 | unidentified | no translation-data target in this block yet | - | - |
| 25 | `0x056C6-0x056CA` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 26 | `0x056CB-0x056CF` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 27 | `0x056D0-0x056D4` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 28 | `0x056D5-0x056DE` | 9 | event/dialogue-related | static-candidate+ppu-sequence | `0x056DA` event/dialogue-related はし (Hashi) `9A 8C` | applied, PPU ambiguous |
| 29 | `0x056DF-0x056E2` | 3 | unidentified | no translation-data target in this block yet | - | - |
| 30 | `0x056E4-0x056E8` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 31 | `0x056E9-0x056F2` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 32 | `0x056F3-0x056F7` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 33 | `0x056F8-0x056FC` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 34 | `0x056FD-0x05701` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 35 | `0x05702-0x0570B` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 36 | `0x0570C-0x05715` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 37 | `0x05716-0x05724` | 14 | event/dialogue-related | static-candidate+ppu-sequence | `0x0571C` event/dialogue-related はし (Hashi) `92 84` | applied, PPU ambiguous |
| 38 | `0x05725-0x05729` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 39 | `0x0572A-0x05738` | 14 | unidentified | no translation-data target in this block yet | - | - |
| 40 | `0x05739-0x0573D` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 41 | `0x0573E-0x05742` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 42 | `0x05743-0x05747` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 43 | `0x05748-0x0574B` | 3 | unidentified | no translation-data target in this block yet | - | - |
| 44 | `0x0574D-0x05751` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 45 | `0x05752-0x05756` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 46 | `0x05757-0x05760` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 47 | `0x05761-0x05765` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 48 | `0x05766-0x0576A` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 49 | `0x0576B-0x0576F` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 50 | `0x05770-0x05774` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 51 | `0x05775-0x0577E` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 52 | `0x0577F-0x05783` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 53 | `0x05784-0x05787` | 3 | unidentified | no translation-data target in this block yet | - | - |
| 54 | `0x05789-0x0578C` | 3 | unidentified | no translation-data target in this block yet | - | - |
| 55 | `0x0578E-0x05792` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 56 | `0x05793-0x05797` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 57 | `0x05798-0x0579C` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 58 | `0x0579D-0x057A6` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 59 | `0x057A7-0x057AB` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 60 | `0x057AC-0x057BA` | 14 | unidentified | no translation-data target in this block yet | - | - |
| 61 | `0x057BB-0x057C4` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 62 | `0x057C5-0x057C9` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 63 | `0x057CA-0x057CE` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 64 | `0x057CF-0x057D3` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 65 | `0x057D4-0x057D8` | 4 | event/dialogue-related | static-candidate+pointer+ppu-sequence | `0x057D4` event/dialogue-related はし (Hashi) `A6 98` | applied, PPU ambiguous |
| 66 | `0x057D9-0x057DD` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 67 | `0x057DE-0x057E2` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 68 | `0x057E3-0x057E7` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 69 | `0x057E8-0x057F6` | 14 | unidentified | no translation-data target in this block yet | - | - |
| 70 | `0x057F7-0x05800` | 9 | unidentified | no translation-data target in this block yet | - | - |
| 71 | `0x05801-0x05805` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 72 | `0x05806-0x0580A` | 4 | unidentified | no translation-data target in this block yet | - | - |
| 73 | `0x0580B-0x05810` | 5 | unidentified | no translation-data target in this block yet | - | - |

## PPU-Ambiguous v0.4 Matches

The following blocks contain targets whose patched byte sequence appeared in the v0.4 PPU stream. All current matches share the same `8B 8C` byte sequence, so this confirms screen/PPU visibility of that sequence but not the exact source ROM offset.

| block | ROM hit | ROM range | expected patched bytes | status |
| ---: | --- | --- | --- | --- |
| 1 | `0x0561A` | `0x05610-0x0561F` | `8B 8C` | applied / ambiguous shared sequence |
| 21 | `0x0569D` | `0x0569C-0x0569F` | `8B 8C` | applied / ambiguous shared sequence |
| 28 | `0x056DA` | `0x056D5-0x056DE` | `8B 8C` | applied / ambiguous shared sequence |
| 37 | `0x0571C` | `0x05716-0x05724` | `8B 8C` | applied / ambiguous shared sequence |
| 65 | `0x057D4` | `0x057D4-0x057D8` | `8B 8C` | applied / ambiguous shared sequence |

## Remaining Gaps

- Menu/title/mode strings are still not identified inside this `ROM+0x05610-0x05810` block map.
- No block in this watch range has runtime active-byte read evidence yet; the runtime-confirmed Bank 1 targets remain outside this narrow range.
- The v0.4 PPU matches prove patched bytes reached the PPU stream, but shared two-byte sequences prevent offset-level proof for the five matched blocks.
- Blocks marked `unidentified` need broader runtime capture, better scene routing, or additional translation-data matching before they can be treated as real user-visible text.

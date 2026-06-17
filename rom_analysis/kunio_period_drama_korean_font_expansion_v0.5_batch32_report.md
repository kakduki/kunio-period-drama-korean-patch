# Font Expansion Candidate Report

- Candidate: **v0.5 font-expansion batch 32**
- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Patched ROM MD5: `af14a5b03d3b6b8631a1bed90cf4295e`
- Glyphs written: **50**
- Added glyphs: **32**
- Changed bytes: **674**
- Added glyph changed bytes: **422**
- IPS records: **103**
- Escaped CHR Bank 07 bytes: **0**
- Local ROM: `output\kunio_period_drama_korean_font_expansion_v0.5_batch32.nes`
- Local IPS: `output\kunio_period_drama_korean_font_expansion_v0.5_batch32.ips`

## Added Glyphs

| glyph | tile | PRG byte (+0x7A) | rows needing it |
| --- | --- | --- | ---: |
| 마 | `0x113` | `0x99` | 14 |
| 하 | `0x114` | `0x9A` | 11 |
| 구 | `0x115` | `0x9B` | 11 |
| 기 | `0x116` | `0x9C` | 11 |
| 의 | `0x117` | `0x9D` | 9 |
| 로 | `0x118` | `0x9E` | 9 |
| 스 | `0x119` | `0x9F` | 8 |
| 강 | `0x11A` | `0xA0` | 7 |
| 지 | `0x11B` | `0xA1` | 6 |
| 인 | `0x11C` | `0xA2` | 6 |
| 가 | `0x11D` | `0xA3` | 6 |
| 에 | `0x11E` | `0xA4` | 6 |
| 니 | `0x11F` | `0xA5` | 5 |
| 쿠 | `0x120` | `0xA6` | 5 |
| 쇠 | `0x121` | `0xA7` | 5 |
| 철 | `0x122` | `0xA8` | 5 |
| 옷 | `0x123` | `0xA9` | 5 |
| 고 | `0x124` | `0xAA` | 5 |
| 간 | `0x125` | `0xAB` | 5 |
| 술 | `0x126` | `0xAC` | 5 |
| 방 | `0x127` | `0xAD` | 4 |
| 어 | `0x128` | `0xAE` | 4 |
| 둥 | `0x129` | `0xAF` | 4 |
| 몽 | `0x12A` | `0xB0` | 4 |
| 파 | `0x12B` | `0xB1` | 4 |
| 슬 | `0x12C` | `0xB2` | 4 |
| 도 | `0x12D` | `0xB3` | 4 |
| 야 | `0x12E` | `0xB4` | 4 |
| 대 | `0x12F` | `0xB5` | 3 |
| 크 | `0x130` | `0xB6` | 3 |
| 게 | `0x131` | `0xB7` | 3 |
| 호 | `0x132` | `0xB8` | 3 |

## Rule

- This candidate expands font coverage only; it is not a new text patch release.
- Additional PRG text promotion still requires ROM byte evidence, screen evidence, and length/padding safety.
- Generated `.nes` files are local test artifacts and must not be distributed.

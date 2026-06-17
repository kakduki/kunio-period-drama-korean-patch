# Font Expansion Candidate Report

- Candidate: **v0.5 font-expansion batch 46**
- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Patched ROM MD5: `5e10cabaff7452fe842726194f4ac843`
- Glyphs written: **64**
- Added glyphs: **46**
- Changed bytes: **837**
- Added glyph changed bytes: **585**
- IPS records: **136**
- Escaped CHR Bank 07 bytes: **0**
- Local ROM: `output\kunio_period_drama_korean_font_expansion_v0.5_batch46.nes`
- Local IPS: `output\kunio_period_drama_korean_font_expansion_v0.5_batch46.ips`

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
| 사 | `0x133` | `0xB9` | 3 |
| 검 | `0x134` | `0xBA` | 3 |
| 갑 | `0x135` | `0xBB` | 3 |
| 패 | `0x136` | `0xBC` | 3 |
| 배 | `0x137` | `0xBD` | 3 |
| 신 | `0x138` | `0xBE` | 3 |
| 진 | `0x139` | `0xBF` | 3 |
| 을 | `0x13A` | `0xC0` | 3 |
| 산 | `0x13B` | `0xC1` | 3 |
| 동 | `0x13C` | `0xC2` | 3 |
| 군 | `0x13D` | `0xC3` | 2 |
| 전 | `0x13E` | `0xC4` | 2 |
| 합 | `0x13F` | `0xC5` | 2 |
| 노 | `0x140` | `0xC6` | 2 |

## Rule

- This candidate expands font coverage only; it is not a new text patch release.
- Additional PRG text promotion still requires ROM byte evidence, screen evidence, and length/padding safety.
- Generated `.nes` files are local test artifacts and must not be distributed.

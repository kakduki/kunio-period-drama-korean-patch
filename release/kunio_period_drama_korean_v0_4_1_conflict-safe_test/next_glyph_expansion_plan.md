# Next Glyph Expansion Plan

This is a planning artifact for extending the compact Korean glyph set without running FCEUX autoplay.

## Summary

- Current compact patch glyphs: **18**
- Extra slots still available in `0x101-0x1B5`: **163**
- Ranked missing glyphs: **202**
- Recommended first batch: **32** glyphs

## Batch Simulation

| extra glyphs | total glyphs | ready rows total | newly ready rows |
| ---: | ---: | ---: | ---: |
| 16 | 34 | 17 | 7 |
| 32 | 50 | 25 | 15 |
| 64 | 82 | 50 | 40 |
| 96 | 114 | 74 | 64 |
| 128 | 146 | 94 | 84 |
| 160 | 178 | 115 | 105 |

## First 32 Glyphs

| # | glyph | tile | PRG byte (+0x7A) | rows needing it |
| ---: | --- | --- | --- | ---: |
| 18 | 마 | `0x113` | `0x99` | 14 |
| 19 | 하 | `0x114` | `0x9A` | 11 |
| 20 | 구 | `0x115` | `0x9B` | 11 |
| 21 | 기 | `0x116` | `0x9C` | 11 |
| 22 | 의 | `0x117` | `0x9D` | 9 |
| 23 | 로 | `0x118` | `0x9E` | 9 |
| 24 | 스 | `0x119` | `0x9F` | 8 |
| 25 | 강 | `0x11A` | `0xA0` | 7 |
| 26 | 지 | `0x11B` | `0xA1` | 6 |
| 27 | 인 | `0x11C` | `0xA2` | 6 |
| 28 | 가 | `0x11D` | `0xA3` | 6 |
| 29 | 에 | `0x11E` | `0xA4` | 6 |
| 30 | 니 | `0x11F` | `0xA5` | 5 |
| 31 | 쿠 | `0x120` | `0xA6` | 5 |
| 32 | 쇠 | `0x121` | `0xA7` | 5 |
| 33 | 철 | `0x122` | `0xA8` | 5 |
| 34 | 옷 | `0x123` | `0xA9` | 5 |
| 35 | 고 | `0x124` | `0xAA` | 5 |
| 36 | 간 | `0x125` | `0xAB` | 5 |
| 37 | 술 | `0x126` | `0xAC` | 5 |
| 38 | 방 | `0x127` | `0xAD` | 4 |
| 39 | 어 | `0x128` | `0xAE` | 4 |
| 40 | 둥 | `0x129` | `0xAF` | 4 |
| 41 | 몽 | `0x12A` | `0xB0` | 4 |
| 42 | 파 | `0x12B` | `0xB1` | 4 |
| 43 | 슬 | `0x12C` | `0xB2` | 4 |
| 44 | 도 | `0x12D` | `0xB3` | 4 |
| 45 | 야 | `0x12E` | `0xB4` | 4 |
| 46 | 대 | `0x12F` | `0xB5` | 3 |
| 47 | 크 | `0x130` | `0xB6` | 3 |
| 48 | 게 | `0x131` | `0xB7` | 3 |
| 49 | 호 | `0x132` | `0xB8` | 3 |

## Rows Unlocked By First 32 Glyphs

| section | category | source | korean | length delta |
| --- | --- | --- | --- | ---: |
| 4. 무기 / 장비 | 무기 | はがねのこんぼう | 강철 몽둥이 | -2 |
| 6. 필살기 / 기술 | 기술 | やまたのじゅつ | 야마타의 술 | -1 |
| 4. 무기 / 장비 | 무기 | どうのこんぼう | 구리 몽둥이 | -1 |
| 4. 무기 / 장비 | 무기 | てつのこんぼう | 쇠 몽둥이 | -2 |
| 7. 보스 / 적 | 보스 | やごろう | 야고로 | -1 |
| 8. 스테이지 | 스테이지 | かじや | 대장간 | 0 |
| 5. 회복 / 보조 아이템 | 회복 | きのくすり | 기의 약 | -1 |
| 4. 무기 / 장비 | 무기 | こんぼう | 몽둥이 | -1 |
| 4. 무기 / 장비 | 무기 | はがねのやり | 강철 창 | -2 |
| 8. 스테이지 | 스테이지 | かわら | 강가 | -1 |
| 3. 스테이터스 / UI | 능력치 | ぼうぎょ | 방어 | -2 |
| 7. 보스 / 적 | 보스 | たつじ | 타츠지 | 0 |
| 4. 무기 / 장비 | 무기 | どうのやり | 구리 창 | -1 |
| 4. 무기 / 장비 | 무기 | てつのやり | 쇠 창 | -2 |
| 6. 필살기 / 기술 | 기술 | どすすぺしゃる | 강타 S | -3 |

## Rule

- This does not promote new ROM text patches by itself.
- Use it to choose which Hangul glyphs to add before searching/promoting more translated offsets.
- Text replacement still needs byte evidence, screen evidence, and length/padding safety.

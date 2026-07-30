# Full Script Font Capacity

This report applies the English patch's CHR footprint to the current
Korean 16x16 renderer instead of treating one English tile as one Korean syllable.

## Capacity

- Translation rows: **144**
- Unique Hangul syllables: **220**
- English reference Bank 7 changed tiles: **181**
- Korean 16x16 cost: **4 CHR tiles / 2 source codes per syllable**
- Runtime-proven page: **17 syllables / 34 source codes**
- English-footprint theoretical page ceiling: **45 syllables**
- Absolute minimum pages at proven capacity: **13**
- Absolute minimum pages at theoretical tile capacity: **5**

The English patch can keep one alphabet page because letters are reused globally.
The Korean patch cannot perform a direct byte-for-byte alphabet substitution:
the current script needs scene/page ownership or a different renderer encoding.

## Packing Simulation

| model | capacity | packed pages | rows too large for one page |
| --- | ---: | ---: | ---: |
| runtime-proven | 17 | 23 | 0 |
| English-tile theoretical | 45 | 9 | 0 |

The packing result is a lower-bound planning model. Runtime scene grouping,
control bytes, menus, and mapper lifetime can only increase the required pages.

## Section Demand

| section | rows | unique Hangul | proven pages minimum | theoretical pages minimum |
| --- | ---: | ---: | ---: | ---: |
| 5. 회복 / 보조 아이템 | 21 | 53 | 4 | 2 |
| 6. 필살기 / 기술 | 24 | 47 | 3 | 2 |
| 12. 기타 | 7 | 46 | 3 | 2 |
| 7. 보스 / 적 | 17 | 36 | 3 | 1 |
| 3. 스테이터스 / UI | 13 | 30 | 2 | 1 |
| 8. 스테이지 | 15 | 27 | 2 | 1 |
| 9. 이벤트 대사 | 9 | 27 | 2 | 1 |
| 1. 타이틀 / 메뉴 | 4 | 26 | 2 | 1 |
| 4. 무기 / 장비 | 21 | 24 | 2 | 1 |
| 2. 메뉴 | 5 | 18 | 2 | 1 |
| 11. 특수 | 3 | 12 | 1 | 1 |
| 10. 엔딩 | 5 | 11 | 1 | 1 |

## Decision

- Reuse the English 248-entry pointer relocation model for text ownership and record packing.
- Do not reuse the English one-page alphabet assumption for Korean glyph storage.
- The next compiler input must assign every translated record to a declared font page.
- A page can be promoted only after its mapper activation and restore boundary pass runtime checks.

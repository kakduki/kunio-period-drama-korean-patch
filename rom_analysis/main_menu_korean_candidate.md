# Korean Main Menu 16x16 Candidate

Status: **CANDIDATE_BUILT_PENDING_BOUNDED_MENU_SMOKE**

## Scoped Change

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Menu template: `0x1F2C1` -> PPU `0x2700`.
- Fixed raster R1: `0x3E` -> `0x46` at `0xEE4D`.
- CHR pair clone: `0x3E` -> `0x46`.
- The original Bank 7 CHR pair is preserved; only the cloned Bank 8 pair receives Korean tiles.
- English patch use: structural menu-slot and font-page evidence, not text or artwork reuse.

## Labels

| id | Korean | column | tile rows |
| --- | --- | ---: | --- |
| `items` | 물건 | 2 | 24-25 |
| `status` | 상태 | 9 | 24-25 |
| `growth` | 성장 | 16 | 24-25 |
| `tech` | 기술 | 23 | 24-25 |
| `record` | 기록 | 2 | 26-27 |
| `ally` | 동료 | 9 | 26-27 |
| `setting` | 설정 | 16 | 26-27 |
| `save` | 저장 | 23 | 26-27 |

## Candidate

- Candidate MD5: `de688d4bf18760cc4fa0682fee5571df`.
- Declared changed spans: `129`.

## Limits

- The fixed raster split is shared outside the menu, so other screens remain UNKNOWN.
- Only the bounded menu route is eligible for this candidate's initial smoke test.
- Menu cursor movement and return lifecycle need separate screen-context checks.

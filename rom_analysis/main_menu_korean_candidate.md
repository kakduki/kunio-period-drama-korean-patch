# Korean Main Menu 16x16 Candidate

Status: **CANDIDATE_BUILT_PENDING_BOUNDED_CROSS_SCREEN_SMOKE**

## Scoped Change

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Menu template: `0x1F2C1` -> PPU `0x2700`.
- Fixed raster R1: `0x3E` -> `0x46` at `0xEE4D`.
- CHR pair clone: `0x3E` -> `0x46`.
- The original Bank 7 CHR pair is preserved; only the cloned Bank 8 pair receives Korean tiles.
- Korean tiles use an isolated non-contiguous code pool; the bounded Items high-code set is excluded.
- English patch use: structural menu-slot and font-page evidence, not text or artwork reuse.
- Korean font quality gate: **PASS**.

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

- Candidate MD5: `d425814e4f1249e2872c9eb09f7fb93d`.
- Declared changed spans: `137`.

## Limits

- The isolated pool is proven only against the bounded Japanese/English menu and Items nametables.
- The fixed R1 clone remains a soft-gated shared renderer change; dialogue, status, and gameplay contexts are not audited.
- This ROM is a bounded candidate until both menu and Items captures pass with lua_done.

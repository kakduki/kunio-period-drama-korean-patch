# Full Korean Pre-Pointer High-Code Candidate

- Candidate MD5: `50617961a99d43be949cc28e2ff092a5`.
- Fixed high-code source rows: `10`.
- Korean high-code glyphs: `9`; code range `0x81-0x89`.
- IPS records: `940`; static scope and IPS construction completed.
- English owner contract: Bank 1 fixed records, 0x81-0x9A input codes, Bank 7 8x16 top/bottom tiles.
- Runtime status: `PASS_CPU_OWNER_PPU_CAPTURE_VISUAL_UNKNOWN` at frame 900; release status: `NOT_READY`.

| record | offset | English | Korean | new bytes |
| --- | --- | --- | --- | --- |
| EN-PRE-112 | `0x05AEB` | BMPKNART<FF> | 기술 | `81 82 FF FF FF FF FF FF FF` |
| EN-PRE-118 | `0x05B1B` | WARPSHOT<FF> | 파 | `83 FF FF FF FF FF FF FF FF` |
| EN-PRE-119 | `0x05B24` | DEFLECT<FF> | 사 | `84 FF FF FF FF FF FF FF` |
| EN-PRE-125 | `0x05B4E` | UDON<FF> | 동 | `85 FF FF FF FF` |
| EN-PRE-129 | `0x05B61` | TENPURA<FF> | 전 | `86 FF FF FF FF FF FF FF` |
| EN-PRE-130 | `0x05B69` | DANGO<FF> | 고 | `87 FF FF FF FF FF` |
| EN-PRE-134 | `0x05B85` | SALVE<FF> | 고 | `87 FF FF FF FF FF` |
| EN-PRE-135 | `0x05B8B` | POULTICE<FF> | 약 | `88 FF FF FF FF FF FF FF FF` |
| EN-PRE-138 | `0x05BA2` | ELIXIR<FF> | 약 | `88 FF FF FF FF FF FF` |
| EN-PRE-185 | `0x05CE0` | KICK<FF> | 타 | `89 FF FF FF FF` |

## Limits

- This is a probe candidate, not a release ROM.
- The shared high-code Bank 7 page must be checked against every other promoted screen.
- The ten selected rows are intentionally separate from control-bearing and missing-glyph rows.

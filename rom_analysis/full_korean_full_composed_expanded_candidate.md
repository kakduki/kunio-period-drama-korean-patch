# Full Korean Pre-Pointer High-Code Candidate

- Candidate MD5: `47637ac3f85a1458d29a285c926d30da`.
- Fixed high-code source rows: `22`.
- Korean high-code glyphs: `26`; code range `0x81-0x9A`.
- IPS records: `526`; static scope and IPS construction completed.
- English owner contract: Bank 1 fixed records, 0x81-0x9A input codes, Bank 7 8x16 top/bottom tiles.
- Runtime status: pending bounded route; release status: `NOT_READY`.

| record | offset | English | Korean | new bytes |
| --- | --- | --- | --- | --- |
| EN-PRE-104 | `0x05AAD` | SCREW<FF> | 회 | `81 FF FF FF FF FF` |
| EN-PRE-105 | `0x05AB3` | TORNADO<FF> | 회리 | `81 82 FF FF FF FF FF FF` |
| EN-PRE-107 | `0x05AC2` | HELICPTR<FF> | 헬기 | `83 84 FF FF FF FF FF FF FF` |
| EN-PRE-108 | `0x05ACB` | DRILL<FF> | 드릴 | `85 86 FF FF FF FF` |
| EN-PRE-111 | `0x05AE2` | HEADBUTT<FF> | 박치기 | `87 88 84 FF FF FF FF FF FF` |
| EN-PRE-112 | `0x05AEB` | BMPKNART<FF> | 기술 | `84 89 FF FF FF FF FF FF FF` |
| EN-PRE-116 | `0x05B0B` | MASSAGE<FF> | 안마 | `8A 8B FF FF FF FF FF FF` |
| EN-PRE-117 | `0x05B13` | BIGBANG<FF> | 빅뱅 | `8C 8D FF FF FF FF FF FF` |
| EN-PRE-118 | `0x05B1B` | WARPSHOT<FF> | 파 | `8E FF FF FF FF FF FF FF FF` |
| EN-PRE-119 | `0x05B24` | DEFLECT<FF> | 사 | `8F FF FF FF FF FF FF FF` |
| EN-PRE-122 | `0x05B3D` | PICKLE<FF> | 피클 | `90 91 FF FF FF FF FF` |
| EN-PRE-123 | `0x05B44` | MEAL<FF> | 밥 | `92 FF FF FF FF` |
| EN-PRE-124 | `0x05B49` | SOBA<FF> | 소 | `93 FF FF FF FF` |
| EN-PRE-125 | `0x05B4E` | UDON<FF> | 동 | `94 FF FF FF FF` |
| EN-PRE-129 | `0x05B61` | TENPURA<FF> | 전 | `95 FF FF FF FF FF FF FF` |
| EN-PRE-130 | `0x05B69` | DANGO<FF> | 고 | `96 FF FF FF FF FF` |
| EN-PRE-131 | `0x05B6F` | RICEBALL<FF> | 주먹밥 | `97 98 92 FF FF FF FF FF FF` |
| EN-PRE-133 | `0x05B7F` | SUSHI<FF> | 밥 | `92 FF FF FF FF FF` |
| EN-PRE-134 | `0x05B85` | SALVE<FF> | 고 | `96 FF FF FF FF FF` |
| EN-PRE-135 | `0x05B8B` | POULTICE<FF> | 약 | `99 FF FF FF FF FF FF FF FF` |
| EN-PRE-138 | `0x05BA2` | ELIXIR<FF> | 약 | `99 FF FF FF FF FF FF` |
| EN-PRE-185 | `0x05CE0` | KICK<FF> | 타 | `9A FF FF FF FF` |

## Limits

- This is a probe candidate, not a release ROM.
- The shared high-code Bank 7 page must be checked against every other promoted screen.
- The 22 selected rows are intentionally bounded; control-bearing and excluded missing-glyph rows remain untouched.

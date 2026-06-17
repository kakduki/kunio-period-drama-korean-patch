# Broad Scan Patchability

This report filters broad-scan hits into future v0.5 candidates.
A row here still needs real screen proof before it should be patched.

## Summary

- Queued broad-scan hits: **60**
- Promotion candidates after screen proof: **7**
- Existing required glyphs: **18**
- Additional glyphs if promoted: **3**
- v0.4.2 glyphs available: **50**
- Promotion candidates font-ready after v0.4.2: **7**
- Additional glyphs still needed after v0.4.2: **0**
- Available CHR patch slots: **181**

## Promotion Candidates After Screen Proof

| confidence | source | korean | ROM | bank | original bytes | v0.4.2 planned bytes | glyphs | missing after v0.4.2 |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| high | へいしち | 헤이시치 | `0x06294` | 1 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | 헤이시치 | - |
| high | へいしち | 헤이시치 | `0x06359` | 1 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | 헤이시치 | - |
| high | へいしち | 헤이시치 | `0x0631B` | 1 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | 헤이시치 | - |
| medium | たつじ | 타츠지 | `0x052A5` | 1 | `82 84 7E` | `0x89 0x98 0xA1` | 타츠지 | - |
| medium | かじや | 대장간 | `0x0440C` | 1 | `CA D0 E9` | `0xB5 0x93 0xAB` | 대장간 | - |
| medium | たつじ | 타츠지 | `0x05BE5` | 1 | `97 99 93` | `0x89 0x98 0xA1` | 타츠지 | - |
| medium | たつじ | 타츠지 | `0x048F4` | 1 | `07 09 03` | `0x89 0x98 0xA1` | 타츠지 | - |

## Compact Base-Plan Glyph Slots If Promoted

| slot | glyph | tile | planned PRG byte | used by ROM offsets |
| ---: | --- | --- | --- | --- |
| 18 | 지 | `0x113` | `0x99` | 0x052A5, 0x05BE5, 0x048F4 |
| 19 | 대 | `0x114` | `0x9A` | 0x0440C |
| 20 | 간 | `0x115` | `0x9B` | 0x0440C |

## Blocked Examples

| source | korean | ROM | bytes | blockers |
| --- | --- | --- | --- | --- |
| 賭場でお金稼ぎ | 도박장에서 돈벌이 | `0x06499` | `93 85 87` | length mismatch source_bytes=3 korean_glyphs=8 |
| 賭場でお金稼ぎ | 도박장에서 돈벌이 | `0x07450` | `93 85 87` | length mismatch source_bytes=3 korean_glyphs=8 |
| はかば | 묘지 | `0x0560E` | `96 82 96` | length mismatch source_bytes=3 korean_glyphs=2 |
| はやし | 숲 | `0x0637B` | `A3 AE 95` | length mismatch source_bytes=3 korean_glyphs=1 |
| チェーン | 체인 | `0x07587` | `90 83 AE` | length mismatch source_bytes=3 korean_glyphs=2 |
| 賭場でお金稼ぎ | 도박장에서 돈벌이 | `0x0589C` | `A6 98 9A` | length mismatch source_bytes=3 korean_glyphs=8 |
| とざん | 등산 | `0x060BD` | `8B 82 A6` | length mismatch source_bytes=3 korean_glyphs=2 |
| まけた… | 졌다… | `0x04242` | `28 11 18` | length mismatch source_bytes=3 korean_glyphs=2 |
| はかば | 묘지 | `0x05F67` | `B3 9F B3` | length mismatch source_bytes=3 korean_glyphs=2 |
| おかね | 돈 | `0x0F3D1` | `04 05 17` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| おかね | 돈 | `0x095B9` | `C7 C8 DA` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| ちから | 힘 | `0x17D61` | `87 7C 9E` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| ちから | 힘 | `0x17D69` | `87 7C 9E` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| ちから | 힘 | `0x17D81` | `87 7C 9E` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| たつじ | 타츠지 | `0x1CB80` | `17 19 13` | not Bank 1; capture priority 25 is not high enough for promotion |
| おかね | 돈 | `0x0EE3D` | `0C 0D 1F` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| おわり | 끝 | `0x10921` | `61 89 85` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| たべる | 먹다 | `0x11332` | `F6 03 10` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=2; capture priority 25 is not high enough for promotion |
| うごき | 움직임 | `0x17D18` | `78 7F 7C` | not Bank 1; capture priority 25 is not high enough for promotion |
| おわり | 끝 | `0x02999` | `A9 D1 CD` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| おかね | 돈 | `0x09830` | `76 77 89` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| すてる | 버리다 | `0x0CEAD` | `0A 10 27` | not Bank 1; capture priority 25 is not high enough for promotion |
| レベル | 레벨 | `0x1281B` | `0F 01 0E` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=2; capture priority 25 is not high enough for promotion |
| おわり | 끝 | `0x1F0B1` | `C5 ED E9` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| たべる | 먹다 | `0x1FA3C` | `F6 03 10` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=2; capture priority 25 is not high enough for promotion |
| うごき | 움직임 | `0x02D68` | `4F 56 53` | not Bank 1; capture priority 25 is not high enough for promotion |
| おかね | 돈 | `0x0966F` | `76 77 89` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| たつじ | 타츠지 | `0x10561` | `1A 1C 16` | not Bank 1; capture priority 25 is not high enough for promotion |
| おかね | 돈 | `0x10D75` | `04 05 17` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| おかね | 돈 | `0x10FD5` | `02 03 15` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=1; capture priority 25 is not high enough for promotion |
| たべる | 먹다 | `0x11340` | `F6 03 10` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=2; capture priority 25 is not high enough for promotion |
| たつじ | 타츠지 | `0x1ADBD` | `1A 1C 16` | not Bank 1; capture priority 25 is not high enough for promotion |
| たつじ | 타츠지 | `0x131F0` | `00 02 FC` | not Bank 1; source bytes contain control-like values; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| まけた… | 졌다… | `0x0A255` | `F0 D9 E0` | not Bank 1; source bytes contain control-like values; length mismatch source_bytes=3 korean_glyphs=2; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| はたけ | 밭 | `0x12F21` | `11 07 00` | not Bank 1; source bytes contain control-like values; length mismatch source_bytes=3 korean_glyphs=1; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| じごく | 지옥 | `0x1317F` | `04 02 00` | not Bank 1; source bytes contain control-like values; length mismatch source_bytes=3 korean_glyphs=2; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| じごく | 지옥 | `0x1319D` | `04 02 00` | not Bank 1; source bytes contain control-like values; length mismatch source_bytes=3 korean_glyphs=2; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| じごく | 지옥 | `0x1318D` | `02 00 FE` | not Bank 1; source bytes contain control-like values; length mismatch source_bytes=3 korean_glyphs=2; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| くすり | 약 | `0x1BB7E` | `00 05 21` | not Bank 1; source bytes contain control-like values; length mismatch source_bytes=3 korean_glyphs=1; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| はかば | 묘지 | `0x0D080` | `B2 9E B2` | not Bank 1; length mismatch source_bytes=3 korean_glyphs=2; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |
| たつじ | 타츠지 | `0x16F72` | `03 05 FF` | not Bank 1; source bytes contain control-like values; capture priority 60 is not high enough for promotion; confidence 'low' is not high/medium |

## Rule

- v0.4.2 already includes the first 32 glyph expansion slots, so use the `v0.4.2 planned bytes` column for preview/test patches.
- The minimal `Additional Glyph Slots If Promoted` table is a compact-from-base view, not the byte map used by v0.4.2.
- Do not build a v0.5 ROM from these rows until the corresponding screen dump confirms active bytes.
- Length mismatches and control-like source bytes remain non-promotable from static evidence.

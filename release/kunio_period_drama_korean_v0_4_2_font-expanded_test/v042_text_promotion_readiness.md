# v0.4.2 Text Promotion Readiness

This report shows which broad-scan text candidates are now font-ready under the v0.4.2 expanded glyph set.

## Summary

- Broad promotion candidates: **7**
- Font-ready after v0.4.2: **7**
- Still missing glyphs: **0**
- Non-overlapping font-ready candidates: **4**
- Conflict-alternative font-ready candidates: **3**

## Candidates

| kind | confidence | ROM | source | korean | original bytes | planned bytes | gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `conflict_alternative_needs_manual_screen` | high | `0x06294` | へいしち | 헤이시치 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | manual screen proof with base ROM broad-scan dump |
| `conflict_alternative_needs_manual_screen` | high | `0x06359` | へいしち | 헤이시치 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | manual screen proof with base ROM broad-scan dump |
| `conflict_alternative_needs_manual_screen` | high | `0x0631B` | へいしち | 헤이시치 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | manual screen proof with base ROM broad-scan dump |
| `non_overlapping_needs_manual_screen` | medium | `0x052A5` | たつじ | 타츠지 | `82 84 7E` | `0x89 0x98 0xA1` | manual screen proof with base ROM broad-scan dump |
| `non_overlapping_needs_manual_screen` | medium | `0x0440C` | かじや | 대장간 | `CA D0 E9` | `0xB5 0x93 0xAB` | manual screen proof with base ROM broad-scan dump |
| `non_overlapping_needs_manual_screen` | medium | `0x05BE5` | たつじ | 타츠지 | `97 99 93` | `0x89 0x98 0xA1` | manual screen proof with base ROM broad-scan dump |
| `non_overlapping_needs_manual_screen` | medium | `0x048F4` | たつじ | 타츠지 | `07 09 03` | `0x89 0x98 0xA1` | manual screen proof with base ROM broad-scan dump |

## How To Prove One

1. Open the base Japanese ROM in FCEUX.
2. Manually reach the screen where the candidate text appears.
3. Run `lua/kunio_manual_broad_scan_dump.lua`.
4. Run `python scripts/analyze_broad_scan_manual_dump.py`.
5. Promote only if the byte match and visible screen context agree.

## Rule

- Do not promote these rows from static evidence alone.
- v0.4.2 means glyphs are ready; it does not prove the ROM offset is the visible text instance.

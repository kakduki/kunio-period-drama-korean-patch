# Primary Patch Contents

This report explains what the current primary IPS changes, without bundling any ROM data.

## Summary

- Primary candidate: **v0.4.2 font-expanded**
- Primary IPS: `output\kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips`
- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Expected patched MD5: `ea11dc002a1a7b07682ce00a754b1a61`
- Applied text rows: **10**
- Runtime-confirmed rows: **1**
- PPU/encoding-evidence rows: **1**
- Static candidate rows: **8**
- Total changed bytes versus base ROM: **700**
- IPS records: **113**

## Applied Text Rows

| # | ROM offset | romaji | source | Korean | old bytes | new bytes | evidence | manual status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `0x07227` | Katana | かたな | 카타나 | `8A 94 99` | `88 89 8A` | runtime-confirmed | runtime read confirmed; still needs visual screen review |
| 2 | `0x0569D` | Hashi | はし | 다리 | `A0 92` | `8B 8C` | encoding-exact | PPU/text-sequence evidence; needs visual screen review |
| 3 | `0x0561A` | Hashi | はし | 다리 | `96 88` | `8B 8C` | static-candidate+pointer | static candidate; needs manual screen proof |
| 4 | `0x05643` | Heishichi | へいしち | 헤이시치 | `9D 82 8C 91` | `8D 8E 8F 90` | static-candidate+pointer | static candidate; needs manual screen proof |
| 5 | `0x057D4` | Hashi | はし | 다리 | `A6 98` | `8B 8C` | static-candidate+pointer | static candidate; needs manual screen proof |
| 6 | `0x0736A` | Raifu | ライフ | 라이프 | `BB 95 AF` | `96 8E 97` | static-candidate+pointer | static candidate; needs manual screen proof |
| 7 | `0x0739D` | Raifu | ライフ | 라이프 | `BB 95 AF` | `96 8E 97` | static-candidate+pointer | static candidate; needs manual screen proof |
| 8 | `0x0562F` | Tatsuichi | たついち | 타츠이치 | `90 92 82 91` | `89 98 8E 90` | static-candidate | static candidate; needs manual screen proof |
| 9 | `0x056DA` | Hashi | はし | 다리 | `9A 8C` | `8B 8C` | static-candidate | static candidate; needs manual screen proof |
| 10 | `0x0571C` | Hashi | はし | 다리 | `92 84` | `8B 8C` | static-candidate | static candidate; needs manual screen proof |

## Notes

- The primary candidate is still for manual testing, not a final release.
- Rows with runtime or PPU evidence still need visible-screen confirmation in FCEUX.
- Static rows should be treated as hypotheses until their exact screen is reached and dumped.
- Shortened replacements and broad-scan conflicts are excluded from v0.4.2 on purpose.

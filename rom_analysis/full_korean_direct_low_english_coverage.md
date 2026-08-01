# English-to-Korean Change Coverage

This is an offset-ownership audit. Same-offset coverage is not semantic or visual proof; relocated Korean records may legitimately have lower overlap.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- English reference IPS: `tools\reference\TSe-v10.ips`.
- Korean candidate: `output\full_korean_direct_low_candidate\kunio_period_drama_korean_full_direct_low_candidate.nes`.
- English changed bytes: `12582`.
- Korean changed bytes inside English record spans: `6650`.
- Same-offset covered bytes: `6013`.
- Records: `99`; covered `7`; partial `19`; missing `73`.

## Records

| record | region | bank | classification | English bytes | Korean bytes | same offset | ratio | status |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| 0 | header | - | header | 1 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 1 | PRG | 1 | renderer_support | 27 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 2 | PRG | 1 | name_table | 135 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 3 | PRG | 1 | prepointer_text | 1470 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 4 | PRG | 1 | dialogue_pointer_table+pointer_driven_text | 6208 | 4540 | 4268 | 0.69 | PARTIAL_SAME_OFFSETS |
| 5 | PRG | 1 | growth_ui | 20 | 18 | 17 | 0.85 | PARTIAL_SAME_OFFSETS |
| 6 | PRG | 1 | menu_or_label | 52 | 54 | 51 | 0.98 | PARTIAL_SAME_OFFSETS |
| 7 | PRG | 1 | menu_or_label | 22 | 24 | 22 | 1.00 | COVERED_SAME_OFFSETS |
| 8 | PRG | 3 | other_prg | 5 | 4 | 4 | 0.80 | PARTIAL_SAME_OFFSETS |
| 9 | PRG | 4 | other_prg | 10 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 10 | PRG | 4 | other_prg | 27 | 16 | 16 | 0.59 | PARTIAL_SAME_OFFSETS |
| 11 | PRG | 4 | other_prg | 250 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 12 | PRG | 4 | other_prg | 8 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 13 | PRG | 4 | other_prg | 80 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 14 | PRG | 4 | other_prg | 305 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 15 | PRG | 4 | other_prg | 66 | 12 | 12 | 0.18 | PARTIAL_SAME_OFFSETS |
| 16 | PRG | 4 | other_prg | 16 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 17 | PRG | 4 | other_prg | 128 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 18 | PRG | 4 | other_prg | 11 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 19 | PRG | 4 | other_prg | 110 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 20 | PRG | 4 | other_prg | 2 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 21 | PRG | 6 | other_prg | 4 | 4 | 4 | 1.00 | COVERED_SAME_OFFSETS |
| 22 | PRG | 6 | other_prg | 198 | 113 | 113 | 0.57 | PARTIAL_SAME_OFFSETS |
| 23 | PRG | 6 | other_prg | 7 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 24 | PRG | 6 | other_prg | 11 | 5 | 5 | 0.45 | PARTIAL_SAME_OFFSETS |
| 25 | PRG | 6 | other_prg | 1 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 26 | PRG | 7 | other_prg | 74 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 27 | PRG | 7 | other_prg | 1001 | 417 | 411 | 0.41 | PARTIAL_SAME_OFFSETS |
| 28 | PRG | 7 | other_prg | 2 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 29 | PRG | 7 | other_prg | 1 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 30 | PRG | 7 | other_prg | 1 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 31 | PRG | 7 | other_prg | 23 | 19 | 19 | 0.83 | PARTIAL_SAME_OFFSETS |
| 32 | PRG | 7 | other_prg | 20 | 17 | 17 | 0.85 | PARTIAL_SAME_OFFSETS |
| 33 | CHR | 1 | font_or_tiles | 8 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 34 | CHR | 2 | font_or_tiles | 16 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 35 | CHR | 2 | font_or_tiles | 20 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 36 | CHR | 2 | font_or_tiles | 7 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 37 | CHR | 2 | font_or_tiles | 49 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 38 | CHR | 2 | font_or_tiles | 23 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 39 | CHR | 2 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 40 | CHR | 2 | font_or_tiles | 14 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 41 | CHR | 2 | font_or_tiles | 21 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 42 | CHR | 2 | font_or_tiles | 14 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 43 | CHR | 2 | font_or_tiles | 7 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 44 | CHR | 2 | font_or_tiles | 7 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 45 | CHR | 2 | font_or_tiles | 24 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 46 | CHR | 2 | font_or_tiles | 15 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 47 | CHR | 2 | font_or_tiles | 21 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 48 | CHR | 2 | font_or_tiles | 7 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 49 | CHR | 2 | font_or_tiles | 18 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 50 | CHR | 2 | font_or_tiles | 12 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 51 | CHR | 7 | font_or_tiles | 98 | 182 | 93 | 0.95 | PARTIAL_SAME_OFFSETS |
| 52 | CHR | 7 | font_or_tiles | 96 | 183 | 93 | 0.97 | PARTIAL_SAME_OFFSETS |
| 53 | CHR | 7 | font_or_tiles | 5 | 5 | 5 | 1.00 | COVERED_SAME_OFFSETS |
| 54 | CHR | 7 | font_or_tiles | 208 | 237 | 182 | 0.88 | PARTIAL_SAME_OFFSETS |
| 55 | CHR | 7 | font_or_tiles | 5 | 4 | 4 | 0.80 | PARTIAL_SAME_OFFSETS |
| 56 | CHR | 7 | font_or_tiles | 46 | 73 | 32 | 0.70 | PARTIAL_SAME_OFFSETS |
| 57 | CHR | 7 | font_or_tiles | 2 | 2 | 2 | 1.00 | COVERED_SAME_OFFSETS |
| 58 | CHR | 7 | font_or_tiles | 4 | 4 | 4 | 1.00 | COVERED_SAME_OFFSETS |
| 59 | CHR | 7 | font_or_tiles | 5 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 60 | CHR | 7 | font_or_tiles | 63 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 61 | CHR | 7 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 62 | CHR | 7 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 63 | CHR | 7 | font_or_tiles | 5 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 64 | CHR | 7 | font_or_tiles | 5 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 65 | CHR | 7 | font_or_tiles | 7 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 66 | CHR | 7 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 67 | CHR | 7 | font_or_tiles | 4 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 68 | CHR | 7 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 69 | CHR | 7 | font_or_tiles | 7 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 70 | CHR | 7 | font_or_tiles | 4 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 71 | CHR | 7 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 72 | CHR | 7 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 73 | CHR | 7 | font_or_tiles | 5 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 74 | CHR | 7 | font_or_tiles | 6 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 75 | CHR | 7 | font_or_tiles | 754 | 433 | 401 | 0.53 | PARTIAL_SAME_OFFSETS |
| 76 | CHR | 7 | font_or_tiles | 14 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 77 | CHR | 7 | font_or_tiles | 12 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 78 | CHR | 7 | font_or_tiles | 14 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 79 | CHR | 7 | font_or_tiles | 172 | 151 | 128 | 0.74 | PARTIAL_SAME_OFFSETS |
| 80 | CHR | 7 | font_or_tiles | 6 | 7 | 6 | 1.00 | COVERED_SAME_OFFSETS |
| 81 | CHR | 7 | font_or_tiles | 4 | 4 | 4 | 1.00 | COVERED_SAME_OFFSETS |
| 82 | CHR | 7 | font_or_tiles | 313 | 122 | 100 | 0.32 | PARTIAL_SAME_OFFSETS |
| 83 | CHR | 12 | font_or_tiles | 3 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 84 | CHR | 12 | font_or_tiles | 10 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 85 | CHR | 12 | font_or_tiles | 1 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 86 | CHR | 12 | font_or_tiles | 2 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 87 | CHR | 12 | font_or_tiles | 2 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 88 | CHR | 12 | font_or_tiles | 3 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 89 | CHR | 12 | font_or_tiles | 1 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 90 | CHR | 12 | font_or_tiles | 1 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 91 | CHR | 12 | font_or_tiles | 2 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 92 | CHR | 12 | font_or_tiles | 2 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 93 | CHR | 12 | font_or_tiles | 3 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 94 | CHR | 15 | font_or_tiles | 5 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 95 | CHR | 15 | font_or_tiles | 4 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 96 | CHR | 15 | font_or_tiles | 3 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 97 | CHR | 15 | font_or_tiles | 2 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |
| 98 | CHR | 15 | font_or_tiles | 53 | 0 | 0 | 0.00 | MISSING_SAME_OFFSETS |

## Interpretation

- `COVERED_SAME_OFFSETS` means the candidate changes every English-changed offset in that IPS record; it does not prove that the Korean bytes are correct.
- `PARTIAL_SAME_OFFSETS` is expected for a candidate that implements only one renderer family or relocates records.
- `MISSING_SAME_OFFSETS` identifies English-patch regions with no Korean byte change and therefore a concrete implementation gap.

\n
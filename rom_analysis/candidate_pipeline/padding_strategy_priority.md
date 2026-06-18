# Padding Strategy Priority

This is the next-test priority list for the shortened padding-rule UNKNOWN gate.
It does not approve any shortened replacement for release.

- Recommended strategy: `preserve_tail`
- Recommended candidate ROM: `output/kunio_period_drama_korean_prg_padding_exp_v05_rom_071a4_candidate_82_preserve_tail.nes`
- Recommended risk class: `LOWEST_STRUCTURAL_RISK`
- Release gate status: `UNKNOWN`

| priority | strategy | risk | patched bytes | CPU | active matches | PPU | visual | candidate ROM |
| ---: | --- | --- | --- | --- | ---: | --- | --- | --- |
| 10 | `preserve_tail` | LOWEST_STRUCTURAL_RISK | `87 88 AA` | PASS | 11 | UNKNOWN | UNKNOWN | `output/kunio_period_drama_korean_prg_padding_exp_v05_rom_071a4_candidate_82_preserve_tail.nes` |
| 35 | `pad_00` | LOW_PADDING_BYTE_RISK | `87 00 00` | PASS | 11 | UNKNOWN | UNKNOWN | `output/kunio_period_drama_korean_prg_padding_exp_v05_rom_071a4_candidate_82_pad_00.nes` |
| 55 | `pad_7a` | MEDIUM_VISIBLE_BYTE_RISK | `87 7A 7A` | PASS | 11 | UNKNOWN | UNKNOWN | `output/kunio_period_drama_korean_prg_padding_exp_v05_rom_071a4_candidate_82_pad_7a.nes` |
| 75 | `pad_f8f9` | HIGH_CONTROL_BYTE_RISK | `87 F8 F9` | PASS | 9 | UNKNOWN | UNKNOWN | `output/kunio_period_drama_korean_prg_padding_exp_v05_rom_071a4_candidate_82_pad_f8f9.nes` |
| 95 | `pad_ff` | HIGHEST_TERMINATOR_RISK | `87 FF FF` | PASS | 4 | UNKNOWN | UNKNOWN | `output/kunio_period_drama_korean_prg_padding_exp_v05_rom_071a4_candidate_82_pad_ff.nes` |

## Recommended Next Check

Use the recommended candidate ROM only for a focused PPU/visual padding check.
Do not merge shortened replacements into the normal dev or release candidate until the padding rule has strict PPU or visual acceptance.

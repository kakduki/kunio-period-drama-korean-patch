# CHR Bank 07 Plan Status

This report validates the compact Korean glyph slot allocation and the CHR-byte footprint of the current generated ROMs.

## Summary

- CHR Bank 07 ROM range: `0x2E010-0x3000F`
- Planned patch tile range: `0x101-0x1B5`
- Planned patch ROM range: `0x2F020-0x2FB6F`
- Required Korean glyphs: **18 / 181** available slots
- Actually used slot range: `0x101-0x112` / `0x2F020-0x2F13F`
- Duplicate planned PRG bytes: **0**

## ROM Diff Validation

| ROM | total changed bytes | changed range | CHR Bank7 bytes | CHR Bank7 range | pre-Bank7 bytes | post-Bank7 bytes | escaped font bytes |
| --- | ---: | --- | ---: | --- | ---: | ---: | ---: |
| v0.2 CHR-only | 252 | `0x2F020-0x2F13E` | 252 | `0x2F020-0x2F13E` | 0 | 0 | 0 |
| v0.4 PRG+CHR | 287 | `0x0561A-0x2F13E` | 252 | `0x2F020-0x2F13E` | 35 | 0 | 0 |

## Required Glyph Slots

| glyph | tile | ROM offset | planned PRG byte | used by labels |
| --- | --- | --- | --- | --- |
| 힘 | `0x101` | `0x2F020` | `0x87` | `rom_071a4_candidate_82`, `rom_066fb_candidate_82`, `rom_06845_candidate_82`, `rom_06605_candidate_82`, `rom_06b4a_candidate_82` |
| 카 | `0x102` | `0x2F030` | `0x88` | `rom_07227_candidate_84`, `rom_05644_candidate_7c`, `rom_06295_candidate_7c`, `rom_0631c_candidate_7c`, `rom_0635a_candidate_7c` |
| 타 | `0x103` | `0x2F040` | `0x89` | `rom_07227_candidate_84`, `rom_05644_candidate_7c`, `rom_06295_candidate_7c`, `rom_0631c_candidate_7c`, `watch_rom_0562f_보스_80`, `rom_0635a_candidate_7c` |
| 나 | `0x104` | `0x2F050` | `0x8A` | `rom_07227_candidate_84`, `rom_05644_candidate_7c`, `rom_06295_candidate_7c`, `rom_0631c_candidate_7c`, `rom_0635a_candidate_7c` |
| 다 | `0x105` | `0x2F060` | `0x8B` | `watch_rom_0569d_스테이지_7a`, `watch_rom_0561a_스테이지_7c`, `watch_rom_057d4_스테이지_8c`, `watch_rom_056da_스테이지_80`, `watch_rom_0571c_스테이지_78` |
| 리 | `0x106` | `0x2F070` | `0x8C` | `watch_rom_0569d_스테이지_7a`, `watch_rom_0561a_스테이지_7c`, `watch_rom_057d4_스테이지_8c`, `watch_rom_056da_스테이지_80`, `watch_rom_0571c_스테이지_78` |
| 헤 | `0x107` | `0x2F080` | `0x8D` | `watch_rom_05643_보스_80` |
| 이 | `0x108` | `0x2F090` | `0x8E` | `watch_rom_05643_보스_80`, `rom_0736a_candidate_93`, `rom_0739d_candidate_93`, `watch_rom_0562f_보스_80` |
| 시 | `0x109` | `0x2F0A0` | `0x8F` | `watch_rom_05643_보스_80` |
| 치 | `0x10A` | `0x2F0B0` | `0x90` | `watch_rom_05643_보스_80`, `watch_rom_0562f_보스_80` |
| 창 | `0x10B` | `0x2F0C0` | `0x91` | `rom_05aa3_candidate_77`, `rom_05aa5_candidate_77`, `rom_05bba_candidate_7a`, `rom_05c09_candidate_7a`, `rom_05c69_candidate_7a`, `rom_06839_candidate_7e`, `rom_068c3_candidate_71`, `rom_0691e_candidate_80`, `rom_069c5_candidate_79`, `rom_06bc6_candidate_7b`, `rom_06d1b_candidate_80`, `rom_058fb_candidate_79`, `rom_06001_candidate_7e`, `rom_06479_candidate_7f`, `rom_065b0_candidate_80`, `rom_06a3d_candidate_79`, `rom_06a66_candidate_79`, `rom_06fde_candidate_80`, `rom_0704f_candidate_7a` |
| 약 | `0x10C` | `0x2F0D0` | `0x92` | `rom_05bdf_candidate_7a` |
| 장 | `0x10D` | `0x2F0E0` | `0x93` | `rom_0602e_candidate_8d`, `rom_06bdf_candidate_8d`, `rom_06fa1_candidate_8d` |
| 비 | `0x10E` | `0x2F0F0` | `0x94` | `rom_0602e_candidate_8d`, `rom_06bdf_candidate_8d`, `rom_06fa1_candidate_8d` |
| 돈 | `0x10F` | `0x2F100` | `0x95` | `rom_06de3_candidate_80` |
| 라 | `0x110` | `0x2F110` | `0x96` | `rom_0736a_candidate_93`, `rom_0739d_candidate_93` |
| 프 | `0x111` | `0x2F120` | `0x97` | `rom_0736a_candidate_93`, `rom_0739d_candidate_93` |
| 츠 | `0x112` | `0x2F130` | `0x98` | `watch_rom_0562f_보스_80` |

## Notes

- `escaped font bytes` must remain `0`; otherwise a CHR patch wrote outside CHR Bank 07.
- v0.4 intentionally has PRG changes before CHR Bank 07 because it includes equal-length PRG text experiments in addition to the CHR font plan.
- Planned PRG bytes are valid for renderer paths that use `CHR tile = PRG byte + 0x7A`; shifted-low candidates still need runtime confirmation before final patching.

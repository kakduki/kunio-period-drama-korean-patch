# Patch Candidate Manifest

This manifest separates the current manual-test ROM from one-off experiments.

## Summary

- Base ROM: `rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Primary current test candidate: **v0.4 equal-length static**
- Primary candidate MD5: `e50d9c974d9968170f932a7ed51fe52e`
- Primary IPS: `output\kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.ips`
- Primary IPS applies to same MD5: **yes**
- v0.4/broad conflicts: `rom_analysis\v04_broad_candidate_conflicts.json` (3 overlaps, 3 high-confidence)
- Completion status: **incomplete; needs manual FCEUX screen verification and more text offsets**
- Manual capture queue: `rom_analysis\manual_capture_queue.json` (27 targets)

## Patch Candidates

| name | role | verdict | ROM | MD5 | report MD5 ok | applied | skipped | changed bytes |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| v0.2 font-only | font/glyph experiment | not playable text patch by itself | `output\kunio_period_drama_korean_plan_v0.2.nes` | `416ad32dfc438c8b51a4d0a20028fe81` | yes |  |  |  |
| v0.3 runtime-confirmed equal-length | conservative PRG+CHR experiment | superseded by v0.4 for current testing | `output\kunio_period_drama_korean_prg_plan_v0.3.nes` | `df28465ab0910743f7914ba1e5c63c16` | yes | 1 | 42 | 255 |
| v0.4 equal-length static | current primary manual-test candidate | test in FCEUX, not final release | `output\kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes` | `e50d9c974d9968170f932a7ed51fe52e` | yes | 13 | 30 | 287 |

## Padding Experiments

These are not release candidates. They exist only to test shortened replacement padding behavior.

| strategy | verdict | ROM | MD5 | report MD5 ok |
| --- | --- | --- | --- | --- |
| pad_00 | not final patch candidate | `output\kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_00.nes` | `cdb124b2434a39d9ad3e28f84b651ed1` | yes |
| pad_7a | not final patch candidate | `output\kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_7a.nes` | `4fa3714a8e9a867889ac96d5ca7cbf79` | yes |
| pad_ff | not final patch candidate | `output\kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_ff.nes` | `7cc172c71358c69052869095cd9f252b` | yes |
| pad_f8f9 | not final patch candidate | `output\kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_f8f9.nes` | `2e5f270289b79ff5bd5fca46dd0caee2` | yes |
| preserve_tail | not final patch candidate | `output\kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_preserve_tail.nes` | `ee7504d0f245ad31779eadea45ad0796` | yes |

## Current Rule

- Test `output/kunio_period_drama_korean_prg_plan_v0.4_equal_length_static.nes` first.
- Use `lua/kunio_manual_v04_screen_dump.lua` on manually reached screens.
- Do not treat padding experiment ROMs as patch releases.

# PRG Padding FCEUX Targets

These targets verify that each padding experiment ROM has the expected patched bytes active in the `ROM+0x071A4` CPU record.

- Padding plan: `rom_analysis\prg_padding_experiment_plan.json`
- Build report: `output\kunio_period_drama_korean_prg_padding_exp_build_report.json`
- Strategies: `5`

## Targets

| strategy | target lua | ROM | MD5 | ROM hit | CPU range | Japanese | Korean | old bytes | expected bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pad_00 | `lua\kunio_padding_exp_pad_00_targets.lua` | `kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_00.nes` | `cdb124b2434a39d9ad3e28f84b651ed1` | `0x071A4` | `$B192-$B19C` | ちから (Chikara) | 힘 | `93 88 AA` | `87 00 00` |
| pad_7a | `lua\kunio_padding_exp_pad_7a_targets.lua` | `kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_7a.nes` | `4fa3714a8e9a867889ac96d5ca7cbf79` | `0x071A4` | `$B192-$B19C` | ちから (Chikara) | 힘 | `93 88 AA` | `87 7A 7A` |
| pad_ff | `lua\kunio_padding_exp_pad_ff_targets.lua` | `kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_ff.nes` | `7cc172c71358c69052869095cd9f252b` | `0x071A4` | `$B192-$B19C` | ちから (Chikara) | 힘 | `93 88 AA` | `87 FF FF` |
| pad_f8f9 | `lua\kunio_padding_exp_pad_f8f9_targets.lua` | `kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_f8f9.nes` | `2e5f270289b79ff5bd5fca46dd0caee2` | `0x071A4` | `$B192-$B19C` | ちから (Chikara) | 힘 | `93 88 AA` | `87 F8 F9` |
| preserve_tail | `lua\kunio_padding_exp_preserve_tail_targets.lua` | `kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_preserve_tail.nes` | `ee7504d0f245ad31779eadea45ad0796` | `0x071A4` | `$B192-$B19C` | ちから (Chikara) | 힘 | `93 88 AA` | `87 88 AA` |

## Example Run

```powershell
python scripts/run_fceux_lua_analysis.py --rom output/kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_00.nes --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_padding_exp_pad_00_targets.lua --frames 3600 --timeout 120 --final-output rom_analysis/fceux_padding_exp_pad_00_watch --clean-output --no-dump-hex --no-dump-bin
```

A successful read-watch run should show `active_expected_match=true` for the selected strategy. Visual acceptance still requires checking the status UI in FCEUX.

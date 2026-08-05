# Four-row manifest candidate re-audit (2026-08-05)

## Reproducible build

The candidate was rebuilt from the verified Japanese base and the tracked
manifest. The manifest selected four pointer rows: `OPENING-182` through
`OPENING-185`; the three rows without proven pointer ownership were skipped.

```text
python build.py --input "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --manifest translation\script.csv --output C:\tmp\kunio_manifest_reaudit.nes --patch-output C:\tmp\kunio_manifest_reaudit.ips --report C:\tmp\kunio_manifest_reaudit.json --force
```

| item | value |
| --- | --- |
| base MD5 | `0d406a85285b4de8468f0dab6aad5fe5` |
| candidate size | `368656` |
| candidate MD5 | `b6ae36bb14ac1ba0836e7d02204d4b57` |
| candidate SHA-256 | `dfdf6838663f26e933d63604398b028645622a5f3dc61074e2066239f07f21f7` |
| generated IPS size | `107132` |
| generated IPS MD5 | `88ae9e0bf1b2d12a9dacfe73d4573b41` |
| tracked IPS | `patches/kunio_period_drama_korean_manifest_4row.ips` |

## Native loader verification

Targets were generated from the candidate's own relocated pointer table and
read by FCEUX for 1,900 frames. Result: `PASS_SOURCE_READS`. FCEUX completed
with `lua_done`; the selected record reads were p182 `26/26`, p183 `14/14`,
p184 `13/13`, and p185 `11/11` for `64/64` total bytes. The dialogue ID
progression reached `B7 -> B8 -> B9 -> BA -> BB` without the earlier repeated
`B6` loader stall.

The existing per-row native visual captures for this exact candidate hash are
recorded in `rom_analysis/manifest_native_runtime_gate.md` and pass for all
four rows. This remains a scoped development milestone, not full-game or
release approval: later dialogue, menus, dynamic contexts, natural boss
progression, and whole-game visual coverage remain open.
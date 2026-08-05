# Manifest Batch 190-193 Native Gate (2026-08-05)

## Scope

This bounded promotion tests records `p190-p193` after the verified opening batch `p182-p189`. It uses the 244-row pointer catalog as the source of record ownership, but the promoted build contains only the twelve reviewed rows. The Japanese base ROM remains immutable.

## Promoted candidate

- Main manifest: `translation/script.csv`
- Build recipe: `build.py --manifest translation/script.csv`
- Candidate MD5: `e0f8f2970874da5413fc907b3449947d`
- Candidate SHA-256: `5d5fa58d466d4be761facd2c0dc4d13df3e6d99924c817d1e502cf82f59e2f6c`
- Candidate size: 368656 bytes
- Generated IPS SHA-256: `747bbde774174d4ab55fdc20fbfc16cdd41a874692a8cf202b686e3036c3f6b9`
- Manifest compiler result: 12 applied rows, 3 intentionally skipped menu/unknown rows

## Native runtime evidence

The bounded route reached all four records in the promoted candidate. Each target completed its source-record read and produced writes in the lower dialogue band beginning at PPU nametable `$2302`.

| record | first read | complete read | PPU writes | dialogue-band writes | VRAM range | result |
|---|---:|---:|---:|---:|---|---|
| p190 | 3111 | 3139 | 28 | 28 | `$2302-$2365` | PASS |
| p191 | 3401 | 3433 | 32 | 32 | `$2302-$2331` | PASS |
| p192 | 3695 | 3715 | 20 | 20 | `$2302-$232B` | PASS |
| p193 | 3977 | 4013 | 36 | 36 | `$2302-$2333` | PASS |

Observed output: `C:\tmp\kunio_main_manifest_190_193_renderer\summary.tsv`. The launcher timeout happened after all four target windows and the Lua `DONE` row were written; the process completion marker was not observed by the launcher, so the bounded runtime evidence is valid while the launcher status is recorded as timeout.

## Gate status

- Source-record read gate: PASS for p190-p193
- Native PPU dialogue-band gate: PASS for p190-p193
- Pixel screenshot gate: UNKNOWN for this development promotion
- Natural gameplay/event/boss route: UNKNOWN
- Full 244-row gameplay regression: UNKNOWN
- Release gate: NOT READY

The four rows are now included in `translation/script.csv` with real pointer-table addresses `0x05F50-0x05F56`. Menu, combat, boss, save/load, and ending contexts remain unverified.

## Reproduction

```powershell
python build.py --input "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --manifest translation\script.csv --output C:\tmp\kunio_main_manifest_12row.nes --patch-output C:\tmp\kunio_main_manifest_12row.ips --report C:\tmp\kunio_main_manifest_12row.json --force
python scripts\generate_manifest_runtime_target.py --candidate C:\tmp\kunio_main_manifest_12row.nes --pointer-index 190 --pointer-index 191 --pointer-index 192 --pointer-index 193 --output C:\tmp\main_manifest_190_193_targets.lua
python scripts\run_fceux_lua_analysis.py --rom C:\tmp\kunio_main_manifest_12row.nes --lua-script lua\kunio_full_pointer_batch_renderer_trace.lua --target-lua C:\tmp\main_manifest_190_193_targets.lua --frames 6000 --timeout 120 --final-output C:\tmp\kunio_main_manifest_190_193_renderer --clean-output --no-stagnation-abort
```
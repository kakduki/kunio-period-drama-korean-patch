# Manifest Batch 194-197 Native Gate (2026-08-06)

## Scope

This bounded batch follows the promoted `p182-p193` opening records. It evaluates `p194-p197` from the full pointer catalog. Only records with both source-read and native PPU dialogue-band evidence are promoted into the main development manifest.

## Main candidate

- Main manifest: `translation/script.csv`
- Applied rows: 14 translated dialogue rows plus 3 intentionally skipped menu/unknown rows
- Candidate MD5: `27894ba832e2b01473c78e9676d6581e1`
- Candidate SHA-256: `411677108c540df5517d3ba0d0cc7f20e1ec287e729a55cc9e86a5fdce8bae35`
- Candidate size: 368656 bytes
- Generated IPS SHA-256: `c06919951faa337276624c022711e522a6250d7b38a812cf480dbc6320d672d8`

## Native runtime gate

The full 244-row candidate reached and rendered p194 and p195. The 14-row main candidate reproduced both records after the manifest promotion.

| record | full candidate complete read | full candidate PPU writes | main candidate complete read | main candidate PPU writes | dialogue-band writes | result |
|---|---:|---:|---:|---:|---:|---|
| p194 | 4229 | 12 | 4287 | 12 | 12 | PASS |
| p195 | 4507 | 16 | 4565 | 16 | 16 | PASS |
| p196 | incomplete; first-read at 5020 was not a complete target match | not applicable | not tested in main | not applicable | not applicable | UNKNOWN |
| p197 | not reached | not applicable | not tested in main | not applicable | not applicable | UNKNOWN |

Both promoted rows wrote to the lower dialogue band beginning at PPU nametable `$2302`. The launcher timeout occurred after the Lua `DONE` row was written; the bounded runtime summaries are retained as evidence.

## Natural route evidence

A separate bounded stage/combat run with dialogue tracing reached gameplay and interaction screens but did not naturally select p196 or p197. Existing combat reports also do not prove an enemy-clear or boss transition. No forced pointer or speculative state write is used to promote these rows.

## Gate status

- p194 source-read gate: PASS
- p194 native PPU gate: PASS
- p195 source-read gate: PASS
- p195 native PPU gate: PASS
- p196: UNKNOWN
- p197: UNKNOWN
- Natural combat/boss route: UNKNOWN
- Full 244-row gameplay regression: UNKNOWN
- Release gate: NOT READY

The main manifest now contains 14 reviewed rows through p195. p196-p197 remain in the draft catalog only until a real route or stronger targeted runtime evidence is obtained.

## Reproduction

```powershell
python build.py --input "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --manifest translation\script.csv --output C:\tmp\kunio_main_manifest_14row.nes --patch-output C:\tmp\kunio_main_manifest_14row.ips --report C:\tmp\kunio_main_manifest_14row.json --force
python scripts\generate_manifest_runtime_target.py --candidate C:\tmp\kunio_main_manifest_14row.nes --pointer-index 194 --pointer-index 195 --output C:\tmp\main_manifest_194_195_targets.lua
python scripts\run_fceux_lua_analysis.py --rom C:\tmp\kunio_main_manifest_14row.nes --lua-script lua\kunio_full_pointer_batch_renderer_trace.lua --target-lua C:\tmp\main_manifest_194_195_targets.lua --frames 6000 --timeout 120 --final-output C:\tmp\kunio_main_manifest_194_195_renderer --clean-output --no-stagnation-abort
```

Observed summary: `C:\tmp\kunio_main_manifest_194_195_renderer\summary.tsv`.
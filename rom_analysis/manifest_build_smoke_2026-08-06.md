# Manifest Build Smoke Report

Date: 2026-08-06

## Build Input

- Base ROM: rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes
- Base size: 262160
- Base CRC32: 014D63C9
- Base MD5: 0d406a85285b4de8468f0dab6aad5fe5
- Base SHA-1: 4338c3001c5e2bf5fad0f282bfee23b79e0ad959
- Base SHA-256: 54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a
- Manifest: translation/script.csv
- Manifest updates: 14
- Manifest skipped: 3 (UNKNOWN ownership/runtime rows)

## Results

- python build.py --manifest: PASS
- Candidate size: 368656
- Candidate CRC32: 5CE2CDFB
- Candidate MD5: 27894ba832e2b01473c78e9676d6581e
- Candidate SHA-1: b7b84a71b10bf13e5e791d385ebd49c4e9527926
- Candidate SHA-256: 411677108c540df5517d3ba0d0cc7f20e1ec287e729a55cc9e86a5fdce8bae35
- Generated IPS size: 107321
- Generated IPS MD5: 7a1d6178fdcbc2b20c5ac4d83c51b058
- Generated IPS SHA-256: c06919951faa337276624c022711e522a6250d7b38a812cf480dbc6320d672d8
- IPS records: 35
- IPS round-trip: PASS; rebuilt candidate SHA-256 matches exactly.

## Runtime Smoke

lua/kunio_main_menu_context_probe.lua was run on the generated candidate with the exact inventory route:

- capture frame: 1960
- extra input: hold A at frames 1900-1911
- lua_start: PASS
- screen capture: PASS
- PPU read tracing: PASS
- lua_done: PASS
- output: C:	mpkunio_manifest_menu_smoke_2026_08_06

The separate opening proof Lua did not complete on the Japanese base within its bounded timeout either. It is classified UNKNOWN_ROUTE_SCRIPT_TIMEOUT, not a candidate boot failure.

## Gate

- Reproducible manifest build: PASS
- Independent IPS generation and round-trip: PASS
- Bounded menu boot/capture: PASS
- Full dialogue native visual coverage: UNKNOWN
- Natural combat/boss/ending route: UNKNOWN
- Release: NOT_READY
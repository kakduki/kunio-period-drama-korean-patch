# Rebuilt Manifest Candidate Smoke (2026-08-06)

## Rebuild Evidence

The fourteen-row `translation/script.csv` manifest was rebuilt from the clean
verified Japanese base with `python build.py`. The generated artifacts were
kept in `C:/tmp` only.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate size: `368656`
- Candidate MD5: `27894ba832e2b01473c78e9676d6581e`
- Candidate SHA-256: `411677108c540df5517d3ba0d0cc7f20e1ec287e729a55cc9e86a5fdce8bae35`
- Generated IPS MD5: `7a1d6178fdcbc2b20c5ac4d83c51b058`
- Manifest updates: `14`; skipped rows: `3`

## FCEUX Smoke

- Candidate: `C:/tmp/kunio_manifest_candidate_2026_08_06.nes`
- Lua: `lua/kunio_stage_progression_probe.lua`
- Frames: `2,400`
- Completion: `lua_done`
- Unique screen fingerprints: `10`
- FC65 slot scans: `649`
- FCEF slot clears: `0`
- Natural boss transition: `UNKNOWN`

## Classification

`PASS_REBUILT_CANDIDATE_BOOT_AND_BOUNDED_ROUTE`

The clean rebuild reproduces the recorded candidate hash and boots through the
bounded route. This is a development soft-gate result only; it does not prove
full native visual coverage, natural combat progression, boss dialogue,
save/load, ending, or release readiness.
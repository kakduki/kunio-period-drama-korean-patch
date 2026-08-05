# Manifest Candidate Recheck (2026-08-06)

## Inputs

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Base size: `262160`
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Translation source: `translation/script.csv`
- Build command: `python build.py --input "rom\\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --output candidate.nes --manifest translation/script.csv --patch-output candidate.ips --report report.json --force`

## Build Result

- Manifest updates: `14`
- Manifest skipped: `3`
- Candidate size: `368656`
- Candidate CRC32: `5CE2CDFB`
- Candidate MD5: `27894ba832e2b01473c78e9676d6581e`
- Candidate SHA-1: `b7b84a71b10bf13e5e791d385ebd49c4e9527926`
- Candidate SHA-256: `411677108c540df5517d3ba0d0cc7f20e1ec287e729a55cc9e86a5fdce8bae35`
- Generated IPS records: `35`
- Generated IPS MD5: `7a1d6178fdcbc2b20c5ac4d83c51b058`
- Build status: `PASS`

## Bounded FCEUX Smoke

The candidate was run with the bounded stage progression probe for 2,400
frames, with the extra dialogue start and combat sweep options enabled.

- Completion: `lua_done`
- Unique screen fingerprints: `10`
- Combat checkpoints: frames `915`, `1049`, `1139`, `1229` and later route samples
- Runtime status: `PASS_BOOT_AND_BOUNDED_COMBAT_ROUTE`
- Natural boss transition: `UNKNOWN_NOT_REACHED`
- Native full-game visual proof: `UNKNOWN`
- Release status: `NOT_READY`

Evidence is kept outside the repository at
`C:/tmp/kunio_manifest_candidate_smoke_2026_08_06` and can be regenerated from
the command above. The candidate ROM and generated IPS remain local artifacts.
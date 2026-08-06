# Full Pointer Candidate Runtime Recheck

Date: 2026-08-06

## Candidate

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM MD5: `165ede9d7cf426a3f8aa841af4268a44`
- Candidate size: `368656` bytes
- IPS MD5: `2c66e0dd6d60248a321e111b85639d43`
- IPS SHA-256: `6045c979b784d0a795e930f8a424406ee71e37a57c779c8a19852e054c07fc77`
- Active translated pointer rows: `244`
- Packed records: `247`
- Planned Korean font pages: `48`

## Static Gates

- Full-pointer compiler test: `PASS`
- Translation/control-skeleton audit: `PASS`
- Layout audit: `PASS`, maximum segment `20/24` cells
- IPS reapply: `PASS`; re-applied bytes equal the candidate
- Full project checks: `PASS`

## Bounded Runtime

The candidate ran with `lua/kunio_stage_progression_probe.lua` and
`KUNIO_EXTRA_DIALOGUE_START=1` for `7200` frames. It completed `lua_done`,
observed `38` screen fingerprints, reached the dialogue transitions, and
entered combat at frame `915`. This confirms bounded gameplay entry for the
new full candidate; it is not full-game or boss-route proof.

A candidate-native visual trace generated targets from the relocated pointer
table. Pointers `182`, `183`, `184`, and `185` matched candidate source bytes
and produced captures at frames `682`, `1019`, `1315`, and `1597`. The launcher
cleanup of that run timed out because the trace's old final summary marker was
not part of the launcher's completion vocabulary. The captures themselves are
valid evidence; cleanup is classified `UNKNOWN`, not gameplay failure.

## Remaining Gates

Natural enemy-clear, boss spawn, boss dialogue, save/load, ending, and
release-wide visual proof remain `UNKNOWN`. This is a development candidate,
not a release artifact.

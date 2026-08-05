# Full Korean unified candidate boot recheck (2026-08-05)

## Candidate

- Candidate: `output/full_korean_unified_candidate/kunio_period_drama_korean_unified_candidate.nes`
- Size: `475152` bytes
- MD5: `7fcf03377cff7536cf7b9a6db735d55e`
- IPS SHA-256: `1d103e503a4f8df8fa67e6fb1223b5262f786d37663d0965c39e805391f4c76d`
- Composition: pointer-owner Korean candidate plus non-pointer overlay; this is a development candidate, not a release artifact.

## Bounded FCEUX run

```text
python scripts/run_fceux_lua_analysis.py --rom output/full_korean_unified_candidate/kunio_period_drama_korean_unified_candidate.nes --lua-script lua/kunio_stage_progression_probe.lua --final-output C:\tmp\kunio_unified_candidate_boot_route --clean-output --frames 1900 --timeout 90 --lua-env KUNIO_EXTRA_DIALOGUE_START=0 --lua-env KUNIO_COMBAT_MIXED=1 --lua-env KUNIO_RAM_TRACE=0 --no-dump-hex --no-dump-bin
```

Result:

- Emulator completion: `lua_done` at frame `1900`.
- Entry route reached combat phase at frame `900`.
- Captured `5` distinct screen fingerprints before the combat loop.
- The route did not repeat the opening-screen fingerprint indefinitely.
- No crash, reset, or mapper failure was observed.
- No natural enemy-clear, boss spawn, or boss dialogue was reached within the bound.

## Gate

`PASS_SOFT_BOOT_AND_COMBAT_ENTRY`, with natural boss/event coverage still `UNKNOWN`.

This evidence proves bounded boot and route entry for the unified development candidate only. It does not authorize release or prove that the non-pointer overlay is visually safe on every context.
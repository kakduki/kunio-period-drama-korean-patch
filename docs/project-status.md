# Project Status

## Scope

This repository builds a reproducible Korean patch candidate for the legally owned Japanese NES/Famicom game. The original ROM, the English-applied ROM, and translated copyrighted English patch text are local inputs or structural references; they are not distributed by this project.

## Confirmed base identity

| Field | Value |
|---|---|
| Platform | NES/Famicom, iNES |
| Base file | `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes` |
| Size | 262,160 bytes |
| Header | `4E 45 53 1A 08 10 41 00 00 00 00 00 00 00 00 00` |
| Mapper | 4 (MMC3), vertical mirroring, no trainer |
| PRG/CHR | 8 x 16 KiB PRG / 16 x 8 KiB CHR |
| CRC32 | `014D63C9` |
| MD5 | `0d406a85285b4de8468f0dab6aad5fe5` |
| SHA-1 | `4338c3001c5e2bf5fad0f282bfee23b79e0ad959` |
| SHA-256 | `54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a` |

## English reference

The local structural reference is `tools/reference/TSe-v10.ips`. Its SHA-256 is `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`. Its PRG, CHR, pointer, renderer, and menu changes are documented in `docs/english-patch-analysis.md` and `rom_analysis/english_patch_implementation_map.md`.

## Current development verdict

- Opening-screen Korean visual proof: `PASS` for the bounded pointer test.
- Fixed labels: `PASS` for 22/22 runtime checks.
- Items action and several byte-level probes: `PASS`.
- Full dialogue and boss-route visual proof: `UNKNOWN`.
- Current clean merged candidate: development-only; release status `NOT_READY`.
- Current known blockers: 57 pre-pointer overflow rows are quarantined and one required glyph is missing in the merged candidate.
- Boss dialogue target queue: 10 structural pointer records; all remain UNKNOWN until a natural event screen is captured.
- Bounded forced renderer probe: 10/10 target pointers were observed; 1/10 (pointer 188) reached text emit/PPU activity, while 9/10 remain UNKNOWN. Natural boss-route proof remains 0/10.

The first usable milestone is one Korean word or label displayed on an actual game screen. The repository already contains that proof; the pipeline now makes it reproducible from the Japanese base.

## Next controlled increment

Add one reviewed row to `translation/script.csv`, build from the clean base with `build.py`, run the bounded runtime test, and record `PASS`, `FAIL`, or `UNKNOWN`. Do not translate or patch every extracted candidate in one pass.

## Latest Reproducibility Evidence

- Authoritative opening candidate MD5: 3384157d7e72f3bf4dd3f742ffe41fc9.
- Bounded FCEUX opening proof: registered 37, source-read hits 37, target_match true, lua_done at frame 883.
- Manifest-driven candidate MD5: 0a983c3d8494444935f000963f415253; one manifest row applied and three skipped as UNKNOWN.
- Manifest candidate bounded route: lua_done, but relocated record source-read hits 0; runtime/visual status UNKNOWN.
- Raw extraction: 248 pointer rows with original bytes and heuristic termination status.
- Default IPS build remains deterministic at candidate MD5 0a983c3d8494444935f000963f415253.
- Full-pointer source rebuild from tracked TSV/JSON/font inputs reproduced the same candidate MD5 and IPS MD5 df8359ea51f9fd36de4c0d2117ad6a9c; external temp output is supported.

## Minimum Feature Recheck (2026-08-05)

The first complete source-built proof was reproduced from the Japanese base using
`text_data/korean_scene_batches/opening_ptr_182_16x16_speaker_separator_proof.json`.
Candidate MD5 is `3384157d7e72f3bf4dd3f742ffe41fc9`; the frame-883 bounded route
matched all 47 target bytes and ended with `lua_done`. The record is pointer 182 at
ROM `0x071B6`, PRG bank 1, CPU `$B1A6-$B1D4`, opening dialogue context. Full details
are in `rom_analysis/minimum_feature_proof_recheck.md`.
## Opening Three-Record Recheck (2026-08-05)

The range-scoped opening candidate was rebuilt from the Japanese base with
`text_data/korean_scene_batches/opening_ptr_182_184_16x16_readability.json`.
The candidate MD5 is `46cedd1da6d49643f5dd6bc4895ce706`, matching the tracked
opening component. Bounded FCEUX runs reached all three records and stopped:

| pointer | ROM record | CPU range | frame | runtime result |
|---|---:|---:|---:|---|
| 182 | `0x071B6` | `$B1A6-$B1C5` | 883 | `target_match=true`, `lua_done` |
| 183 | `0x071D6` | `$B1C6-$B1DE` | 1093 | `target_match=true`, `lua_done` |
| 184 | `0x071EF` | `$B1DF-$B1F5` | 1399 | `target_match=true`, `lua_done` |

This is a bounded opening-dialogue development proof, not a full-game release
approval. The natural combat/boss route and the remaining dialogue records are
still `UNKNOWN`.

## Bounded Stage Map Route Matrix (2026-08-05)

A four-direction bounded probe was run against the current expanded candidate
(MD5 `64b599ca6c502b635d216aebf5ce61b9`). `left`, `right`, and `up` each ended
with `lua_done` after 10 unique screens; `down` ended after 9. All entered
combat, but none produced a confirmed enemy-clear marker, map transition,
boss-spawn state, or natural boss dialogue read. The 7,200-frame right-direction
follow-up also ended finite with 11 unique screens and no boss marker.

The route result is classified as `UNKNOWN_ROUTE_NOT_REACHED`, not a failed ROM
build. Details and next state-contract work are in
`rom_analysis/stage_map_route_matrix.md`.
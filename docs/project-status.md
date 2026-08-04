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

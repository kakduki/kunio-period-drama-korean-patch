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
## Translation Manifest Minimal Build Gate (2026-08-05)

The manifest path was re-run from the verified Japanese base after tightening
`tools/insert_text.py` to treat `translation/script.csv` as an explicit
allow-list. One verified pointer row was compiled, three rows without proven
pointer ownership were skipped, and unselected full-pointer draft rows were
left on the original Japanese path. The candidate was generated successfully
with MD5 `b5afc3e437238cc4e9186f2b19c56214`; the generated IPS MD5 is
`46b7fb8914b7ef31624db97e73635426`. This is a build/runtime development gate;
natural route and native-pixel visual status remain `UNKNOWN`, so release
status remains `NOT_READY`.
The manifest candidate also passed a bounded FCEUX process check: the correct
watcher/target pairing ended `lua_done` at frame 900 with 33 target bytes
registered. It produced 0 source-read hits because that watcher does not inject
the opening route; this is classified `UNKNOWN_ROUTE_NOT_REACHED`, not a ROM
failure. The existing opening proof remains the runtime/visual authority.


## Real-Time Translation Overlay MVP (2026-08-05)
The overlay MVP is now an executable sidecar path. A bounded FCEUX run on the
verified Japanese base emitted `OPENING-182` at frame 656 and
`OPENING-183` at frames 718/1047; `tools/realtime_translation_overlay.py`
resolved the reached rows as `CACHED`. `OPENING-184` is registered but was not
reached before the frame cap. This proves the sidecar handoff for the reached
known records; it does not change the native ROM release status, which remains
`NOT_READY`. See `rom_analysis/realtime_overlay_mvp.md`.


## Map CRSR Route Gate (2026-08-05)
The Map CRSR label is confirmed as pre-pointer record `EN-PRE-167` at ROM
`0x05C69` / CPU `$9C59`, with control byte `0x38`. The standard runtime target
generator excludes it as a `control_skeleton`, and no safe RAM ownership address
has been proven. The similarly named `$9C54` candidate is a different byte pattern
and is not authorized for state writes. Route status remains `UNKNOWN`; details are
in `rom_analysis/map_crsr_route_gate.md`.


## Map CRSR Source-Read Comparison (2026-08-05)
The dedicated bounded probe ran against both the English reference and Japanese
base. Each completed at frame 3600 with 9 target bytes registered, 5 unique
screen fingerprints, and 0 Map CRSR source reads. This is classified as
`UNKNOWN_ROUTE_NOT_REACHED` for both ROMs; no state write or native patch change
was authorized. See `rom_analysis/map_crsr_source_probe.md`.

## Opening Pointer 185 Source Gate (2026-08-05)

A dedicated bounded source probe reached `PTR-185` at frame `1691` after three
explicit dialogue acknowledgements. The exact base record at ROM `0x07208` /
CPU `$B1F8-$B206` produced `15/15` source-read hits, `target_match=true`, a
screen capture, and `lua_done`. This is `PASS` for source ownership and bounded
opening-route reachability. The native Korean visual gate remains `UNKNOWN`.

The real-time overlay recheck now emits all four opening IDs (182-185) in one
1,900-frame bounded run. The p184 target was corrected to its exact base window;
p185 was emitted at frame `1655` and resolved from the cache.

## Native Manifest Runtime Gate (2026-08-05)

The two-row manifest candidate (`03c8abce53e019b39d0efad17c82fe98`) was checked
using targets generated from its own pointer table: p182 relocated to `$9FB4`
and p185 to `$9FCE`. The bounded 1,900-frame opening route produced zero
source-read hits for the generated targets and ended `target_not_seen`. This is
classified `UNKNOWN_CANDIDATE_ROUTE_OR_PRG_MAPPING`; the static build remains
valid, but native relocated runtime is not release evidence. Details are in
`rom_analysis/manifest_native_runtime_gate.md`.

## Corrected Native Manifest Runtime Gate (2026-08-05)

The two-row manifest candidate was rebuilt with the pointer loader's X-register
preservation fix. Its candidate MD5 is `a5432d693a51e682bd23760a76e1c3ad` and
its generated IPS MD5 is `bed2f958208ac945bb4a47dad7826973`. A bounded loader
trace now reaches dialogue IDs `B7 -> B8 -> B9 -> BA` and reads all 37 bytes
owned by selected rows p182/p185. Separate bounded native captures pass for
both rows: p182 at frame 712 (`26/26`, target match true) and p185 at frame
1661 (`11/11`, target match true). This proves the selected development rows,
not the full dialogue/event/boss release. The full release remains `NOT_READY`.
See `rom_analysis/manifest_native_runtime_gate.md`.
## Four-Row Native Manifest Gate (2026-08-05)

The selected manifest now builds p182-p185 together. Candidate MD5 is
`b6ae36bb14ac1ba0836e7d02204d4b57`; generated IPS MD5 is
`88ae9e0bf1b2d12a9dacfe73d4573b41`. Generated candidate targets relocate to
`$9FB4`, `$9FCE`, `$9FDC`, and `$9FE9`. The bounded loader trace reads all 64
selected bytes and reaches `B7 -> B8 -> B9 -> BA -> BB`. Separate native
captures pass for all four rows at frames 712, 1059, 1345, and 1627. Full
248-row coverage, non-pointer contexts, and natural boss routes remain
`UNKNOWN`; release remains `NOT_READY`.

## Same-Input Combat Comparison (2026-08-05)

The English reference and current full Korean candidate were run with the same
6,000-frame sweep/map route. Both entered combat at frame 915, ended with
`lua_done`, and showed no boss transition. The localized screen fingerprints
differ as expected, but the bounded route shape and state checkpoints match.
This is `PASS_FINITE_SAME_GAMEPLAY_NO_BOSS`, not natural enemy-clear or release
proof. Details are in `rom_analysis/combat_route_same_input_comparison.md`.

## Counter-Zero Route Comparison (2026-08-05)

The same bounded 7,200-frame combat route was run against the English reference
and the current full Korean candidate with the new `$AA87` execution trace.
Both runs reached `$7A01=00` at frame 6193, changed `$04F1` from `01` to `03`
at frame 7019, and ended with `lua_done` at frame 7200. `$7A02` remained `00`
in both runs. No confirmed dialogue source/parser/PPU event followed the
counter-zero transition, so this is `UNKNOWN_COUNTER_ZERO_NO_DIALOGUE`, not
boss proof. See `rom_analysis/counter_zero_route_trace.md`.


## Direct Counter-Read Trace (2026-08-05)

The optional direct-read trace was run against both ROMs for 7,200 frames.
Each executed `$AD76` (`LDA $7A01`) exactly twice at frame 1064 with the same
values; `$A661`, `$AD86`, and `$AD89` did not execute. No direct counter read
occurred near the later `$7A01=00` or `$04F1=03` checkpoints. This supports
classifying `$7A01` as a shared route/setup value, not a confirmed enemy HP or
boss-clear variable. The natural boss route remains `UNKNOWN`.
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
- Full pointer sweep: `PASS` for 244/244 active Korean pointer records and 4/4 excluded records. This is bounded forced-renderer evidence, not natural event proof.

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
approval. The full-pointer forced-render sweep is separately `PASS` for 244/244 active rows;
natural combat/boss route proof remains `UNKNOWN`.

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
captures pass for all four rows at frames 712, 1059, 1345, and 1627. Non-pointer
contexts and natural boss routes remain `UNKNOWN`; the 244 active pointer rows have
separate bounded forced-render coverage; release remains `NOT_READY`.

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

## Eight-Row Native PPU Gate (2026-08-05)

The main translation manifest now selects opening rows p182-p189. From the
verified Japanese base, `build.py --manifest translation/script.csv` reproduces
candidate MD5 `e0b450a50083dc9dc67aee10af9d130d` and IPS SHA-256
`d1ff5e14a1829f06e93eff7c76fbe28dc3de9bd18545830e0d64898aeff03e35`.

The renderer-context trace found the lower dialogue nametable at `$2302` and
recorded candidate-specific PPU bytes for all eight rows. Fixed base/candidate
screenshots showed nonzero pixel differences in y=160..240 for every row. The
bounded native visual gate for p182-p189 is `PASS`; menu, combat, boss,
save/load, ending, and full-game release gates remain `UNKNOWN`/`NOT_READY`.
See `rom_analysis/manifest_native_visual_comparison_2026-08-05.md`.
## Twelve-Row Native Promotion (2026-08-05)

The main development manifest now contains twelve reviewed opening dialogue rows, `p182-p193`. Rows `p190-p193` were promoted only after a bounded FCEUX route confirmed complete source reads and lower-dialogue-band PPU writes at `$2302`. Candidate MD5: `e0f8f2970874da5413fc907b3449947d`. Natural gameplay, combat, boss, save/load, ending, and full 244-row regression remain `UNKNOWN`; release status remains `NOT_READY`.

## Fourteen-Row Native Promotion (2026-08-06)

The main development manifest now contains fourteen reviewed opening dialogue rows, `p182-p195`. Rows `p194-p195` passed bounded source-read and native lower-dialogue-band PPU gates. Rows `p196-p197` remain `UNKNOWN` because the bounded natural stage/combat route did not select them; they were not promoted. Release status remains `NOT_READY`.

## Manifest Candidate Recheck (2026-08-06)

The current fourteen-row manifest rebuilt reproducibly from the verified Japanese base with candidate MD5 27894ba832e2b01473c78e9676d6581e and generated IPS MD5 7a1d6178fdcbc2b20c5ac4d83c51b058. A 2,400-frame FCEUX stage-progression smoke completed with lua_done, 10 unique screen fingerprints, and combat checkpoints beginning at frame 915. This is PASS_BOOT_AND_BOUNDED_COMBAT_ROUTE; natural boss transition and full native visual coverage remain UNKNOWN, so release status remains NOT_READY. See rom_analysis/manifest_candidate_recheck_2026-08-06.md.

## Late Pointer Runtime Follow-up (2026-08-06)

p196-p201 were rechecked against the Japanese base with an 800-frame PPU observation window. p197 produced a partial source-read at frame 5384 and 277 writes in `$2023-$22E6`, but no complete record match and zero writes in the lower dialogue band beginning at `$2302`. p196 and p198-p201 were not reached. No rows were promoted; natural boss progression remains UNKNOWN and release remains NOT_READY. See `rom_analysis/late_pointer_runtime_followup_2026-08-06.md`.

## Combat Branch Trace (2026-08-06)

The optional AA80-AA8F execution hook ran for 2,400 frames and completed with `lua_done`. It recorded 181 rows at frames 1060 and 1064; AA87 executed 9 times per frame while `$7A02` remained `$00`, `$7A01` was `$3F`, and `$04F1` was `$01`. Neighboring AA8C/AA8E execution advanced an X-indexed loop. This is diagnostic evidence against treating `$7A02` or `$04F1` as a safe boss cheat, not boss proof. Release remains `NOT_READY`. See `rom_analysis/combat_branch_trace_2026-08-06.md`.

## Combat Object Execution Trace (2026-08-06)

The new optional object-routine trace completed a 2,400-frame Japanese-base run
with lua_done. $8D02 executed 642 times during combat, but $0430/$0431 stayed
$00; changing $0432-$0435 values behaved like object coordinate and render
fields. The $AD31/$AD34 comparison path appeared only during setup. This is
PASS_TRACE_NOT_A_BOSS_FLAG; no cheat target was promoted. Natural boss
progression remains UNKNOWN, and release remains NOT_READY. See
rom_analysis/combat_object_execution_trace_2026-08-06.md.
## Combat Slot-Clear Trace (2026-08-06)

The FC65 slot scan ran in three bounded input variants, but FCEF was never
called: mixed 7,200 frames, grid 3,600 frames, and stationary 3,600 frames.
This confirms that the existing autoplay routes do not perform a real enemy
clear. No counter or slot byte was promoted. Natural boss progression and
later dialogue remain UNKNOWN; release remains NOT_READY. See
rom_analysis/combat_slot_clear_trace_2026-08-06.md.
## Map Entry Input Probe (2026-08-06)

A 1,400-frame input-only probe sent the documented Start -> B encounter-map
sequence after the bounded combat entry, independent of the unresolved
stage-clear state. It completed with `lua_done` and nine screen fingerprints,
but reached neither collision dispatch (`FAD9`) nor slot clearing (`FCEF`), and
no confirmed map transition or boss dialogue appeared. This is
`PASS_INPUT_PROBE_NO_MAP_OR_COLLISION`: the route is not a first-screen hang,
but it is still not a real enemy-clear route. No cheat or candidate promotion
was made; natural boss progression and later dialogue remain `UNKNOWN`, and
release remains `NOT_READY`. See
`rom_analysis/map_entry_input_probe_2026-08-06.md`.

## English Reference Combat Route Comparison (2026-08-06)

The verified Japanese base and the local English reference ROM were run through
the same 3,600-frame mixed combat route. Both completed with `lua_done`, eleven
unique screen fingerprints, 1,234 FC65 slot scans, and zero calls to FAD9
collision dispatch, FC82 slot-clear dispatch, or FCEF slot clearing. The final
fingerprint was identical. This is `PASS_SAME_ROUTE_SHAPE_NO_COLLISION`: the
long-running bounded pattern is not caused by the Korean localization, and the
English patch does not contain a boss warp or complete gameplay macro. Natural
combat, boss dialogue, save/load, ending, and full regression remain `UNKNOWN`;
release remains `NOT_READY`. See
`rom_analysis/english_reference_combat_route_comparison_2026-08-06.md`.

## External Cheat RAM Probe (2026-08-06)

A public cheat hypothesis (`$7A00=$44`, `$7A01=$44`, `$7A02=$00`) was applied
only as per-frame FCEUX RAM writes to the English reference ROM. The run
completed with `lua_done` and eleven screen fingerprints, but recorded 1,235
FC65 scans and zero FAD9 collision dispatches, FC82 slot-clear dispatches, or
FCEF slot clears. Changed fingerprints are not sufficient evidence of a boss
warp or stage-clear flag. Classification is
`PASS_EXTERNAL_CHEAT_PROBE_NO_ROUTE_ADVANCE`; no writes were promoted to the
Korean patch. See `rom_analysis/external_cheat_ram_probe_2026-08-06.md`.

## Object Region Execution Trace (2026-08-06)

An optional `$AD00-$AD7F` execution trace on the English reference ROM found
1,300 repeated `$AD00` object-loop rows, while the `$AD30-$AD7E`
coordinate-table pass produced 78 rows at frame 1064 only. The route also had
634 `$8D02` calls and zero FAD9 collision dispatches, FC82 slot-clear dispatches,
or FCEF clears. Classification is
`PASS_OBJECT_REGION_TRACE_NO_COLLISION`: the visible actor loop is active but
this route does not reach a confirmed enemy-hit/death transition. The new
region option is disabled by default; see
`rom_analysis/object_region_execution_trace_2026-08-06.md`.

## Rebuilt Manifest Candidate Smoke (2026-08-06)

The fourteen-row manifest was rebuilt from the clean verified Japanese base.
The candidate MD5 `27894ba832e2b01473c78e9676d6581e` and generated IPS MD5
`7a1d6178fdcbc2b20c5ac4d83c51b058` match the recorded candidate. A fresh
2,400-frame FCEUX smoke completed with `lua_done`, ten screen fingerprints,
649 FC65 scans, and zero FCEF slot clears. This is
`PASS_REBUILT_CANDIDATE_BOOT_AND_BOUNDED_ROUTE`; full native visual coverage,
natural boss progression, and release remain `UNKNOWN`/`NOT_READY`. See
`rom_analysis/manifest_rebuild_smoke_2026-08-06.md`.

## Full Text Extraction Coverage (2026-08-06)

`tools/extract_text.py` was rerun against the verified Japanese base and
produced all 248 pointer rows. Five rows are absent from the conservative
catalog. The regenerated pointer catalog now matches the current native gate:
14 development-verified opening rows (`PTR-182`-`PTR-195`), 229 structural
unknown rows, and five structural unknown rows missing conservative ownership.
The translation manifest contains 17 development rows in total, including
three menu/action rows, but only the 14 pointer rows enter the native dialogue
candidate. This is `PASS_EXTRACTION_COVERAGE_RECORDED`, not full translation
completion; unknown rows remain intentionally unpatched. See
`rom_analysis/text_extraction_coverage_2026-08-06.md`.

### 2026-08-06 collision-pattern comparison

Two clean Japanese-base FCEUX runs compared stationary mixed attacks with a grid movement attack for 2,400 frames. Both reached the bounded combat-like route and completed with `lua_done`; the runs produced 9 and 10 unique screen fingerprints and 652 and 639 FC65 slot scans respectively. Neither invoked FAD9 collision dispatch, FC82 slot-clear dispatch, or FCEF slot clearing. This is evidence that the current automated inputs do not establish target overlap, not evidence of a safe cheat or a broken Korean candidate. Natural enemy-clear and boss transition remain `UNKNOWN`; release remains `NOT_READY`. See `rom_analysis/combat_attack_pattern_comparison_2026-08-06.md`.
### 2026-08-06 OAM sprite probe

The stage probe now supports `KUNIO_OAM_TRACE=1`, producing 256-byte OAM shadow dumps for each capture. A 1,400-frame grid run completed with `lua_done`, 10 unique screens, and 10 OAM dumps. Frames 1139 and 1229 show multiple sprite clusters with separated screen-space X ranges; no collision dispatch or slot clear occurred. This provides a coordinate-based next diagnostic, not boss or cheat proof. See `rom_analysis/oam_sprite_probe_2026-08-06.md`.
### 2026-08-06 OAM-directed attack sweep

The probe now supports an OAM-directed directional sweep and an A/B mixed-button variant. Two clean Japanese-base 3,600-frame runs reached `lua_done` with 10 unique screens and 1,218/1,211 FC65 scans, but both recorded zero FAD9 collision dispatches, FC82 slot-clear dispatches, and FCEF slot clears. This rules out the narrow wrong-button/fixed-direction hypothesis; natural enemy-clear and boss progression remain `UNKNOWN`. See `rom_analysis/oam_directed_attack_sweep_2026-08-06.md`.
### 2026-08-06 OAM write ownership trace

The stage probe now records post-entry writes to OAM shadow RAM with `KUNIO_OAM_WRITE_TRACE=1`. A 1,400-frame OAM-directed run completed with `lua_done`, 9 unique screens, and 22,380 OAM write rows. The dominant active-sprite writer family was `$8438/$843D/$8442/$8447`, while `$DB32-$DB49` and `$DAEB-$DAF4` were repeated fill paths. This establishes runtime ownership of rendered sprite records but not collision eligibility. See `rom_analysis/oam_write_ownership_trace_2026-08-06.md`.
### 2026-08-06 OAM-to-object source correlation

The OAM trace now includes renderer source bytes `$0010-$0013`, object workspace `$0430-$0437`, `$0706/$07BC/$07E4`, and state candidates `$0028-$002D`. A 1,400-frame run captured 22,380 post-entry writes and repeated workspace signatures at the `$8438` active-sprite writer. This correlates rendered sprite records with runtime object data but does not yet identify player/enemy roles or collision eligibility. See `rom_analysis/oam_object_source_correlation_2026-08-06.md`.
## Translation Coverage Bridge (2026-08-06)

The readable translation reference contains 144 Korean entries. The new
`generate_translation_coverage_bridge.py` report joins those entries to the
current static pattern-scan candidates without promoting them to patch targets:
8 entries intersect known Bank 1 candidates, 16 have unverified static hits,
115 have no current static candidate, and 5 were intentionally skipped by the
scanner. Every row remains `not_runtime_proven`; this is a coverage and triage
artifact, not full translation completion. See
`rom_analysis/translation_coverage_bridge.md`.

### 2026-08-06 Manifest Build Smoke Recheck

The current fourteen-row manifest rebuilt from the verified Japanese base with candidate MD5 27894ba832e2b01473c78e9676d6581e and generated IPS MD5 7a1d6178fdcbc2b20c5ac4d83c51b058. Applying that IPS back to the base reproduced the candidate SHA-256 exactly. The exact inventory menu route completed with lua_done at frame 1960. The separate opening proof script also timed out on the Japanese base, so it is classified UNKNOWN_ROUTE_SCRIPT_TIMEOUT; it is not evidence of a manifest candidate boot failure. Full dialogue, natural combat/boss/ending, and release gates remain UNKNOWN/NOT_READY. See rom_analysis/manifest_build_smoke_2026-08-06.md.
### 2026-08-06 Hashi Route Probe

A 7,200-frame Japanese-base stage/map sweep with dialogue tracing completed with lua_done and ten screen fingerprints. It did not read the Hashi A0 92 source pair and did not show a confirmed collision, enemy-slot clear, map transition, boss marker, or boss dialogue. This is UNKNOWN_ROUTE_NOT_REACHED, not a first-screen hang or ROM failure; no speculative state write was promoted. See rom_analysis/hashi_route_probe_2026-08-06.md.
### 2026-08-06 Targeted Overlap Probe

A dedicated fixed-direction attack probe reached a visible player/enemy overlap at frame 1131 and completed with lua_done. The watched FAD9 collision, FC82 slot-clear, and FCEF clear dispatches were all zero, so those addresses are not yet proven as this interaction's path. No cheat or ROM state write was promoted; the next diagnostic is execution tracing from the attack/object update. See rom_analysis/targeted_overlap_probe_2026-08-06.md.
### 2026-08-06 Target-overlap pulse rerun

The targeted overlap probe was rerun with six-frame A/B attack pulses and changing directions instead of continuously held attack buttons. It completed at frame 2400 with 19 captures and continued to execute the object and slot loops, but FAD9 collision dispatch, FC82 slot-clear dispatch, and FCEF slot clear remained zero. This rules out a simple held-button edge hypothesis; the visible actor roles and natural enemy-clear/boss route remain UNKNOWN. No cheat or RAM write was promoted. See `rom_analysis/targeted_overlap_probe_2026-08-06.md`.
### 2026-08-06 Mode-selection route correction

A native capture showed that frame 900 was the `1P ? COM` / `1P ? 2P` mode-selection screen, not combat. The overlap probe now supports `KUNIO_SELECT_MODE=1`; after confirming the default mode it reached a field/bridge screen at frame 990 and a town/actor screen at frame 1225. A 7,200-frame rerun completed with 66 screen captures, but no known collision/clear dispatch, boss spawn, or dialogue proof. Earlier overlap evidence is therefore downgraded to `PASS_MODE_SELECT_AND_FIELD_ENTRY; UNKNOWN_NATURAL_ENCOUNTER`. See `rom_analysis/targeted_overlap_probe_2026-08-06.md`.


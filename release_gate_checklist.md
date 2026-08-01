# Release Gate Checklist

Current release verdict: **UNKNOWN**

| gate | status | evidence / reason |
| --- | --- | --- |
| Base ROM identity | PASS | MD5 matches the verified Japanese base. |
| English structural reference | PASS | Recorded IPS SHA-256; used only for structure. |
| Scoped three-record opening build | PASS | 129 declared changed spans; 0 escaped bytes; range guard protects pointer 185. |
| Bounded boot and target reads | PASS | 182 frame 883 `32/32`; 183 frame 1093 `25/25`; 184 frame 1399 `23/23`; all `lua_done`. |
| Complete pointer ownership catalog | PASS | English-guided Bank 1 catalog contains all 248 pointer rows; five missing conservative rows are explicitly listed for investigation. |
| Native Korean readability | PASS | Three native 16x16 opening screenshots reviewed. |
| Japanese source context | PASS | Pointer 184 base-ROM capture is recorded; prior opening records already had context evidence. |
| Scoped main-menu build | SOFT_GATE_PASS_ISOLATED_R1_POOL | Menu capture and the bounded Items page-isolation smoke both pass. |
| Items shared-page probe | PASS | ROM -> CPU -> SRAM -> PPU chain is proven; current Korean pool does not overlap the action codes. |
| Menu cursor lifecycle | UNKNOWN | A post-template probe was inconclusive. |
| Other R1 raster contexts | UNKNOWN | Shared split needs per-screen audit. |
| Release-wide Korean glyph capacity | SOFT_GATE_PASS | The optimized 48-page build fits 13 appended CHR banks; forced pointers 0/25/50/110/181 prove pages 10/14/39/30/41 with matching state/R1 and preserved backgrounds. Natural event control and broad scene auditing remain open. |
| Full translated script | CANDIDATE_BUILT | 244 Korean rows compile with preserved English non-letter control skeletons; 14 token-sensitive rows use explicit Korean segments, 244 rows are English-reference reviewed, no translation drafts remain, and four excluded rows retain Japanese bytes. |
| Non-opening pointer batch | UNKNOWN | Pointers 2-3 compile and relocate safely; the bounded opening/extended routes reached no target capture, so early-boss screen context is not yet captured. |
| Direct 8x16 pointer batch | UNKNOWN | Pointers 0-2 compile with 24 glyphs and 0 escaped bytes; boot passes at frame 883, but the frame-5000 route has no complete target match and p0 has a multi-message structural risk. |
| Opening-context Korean glyph capacity | SOFT_GATE_PASS | Pointer 182 proves 34 paired source slots (`0x81-0x9A` plus `0xC0-0xC7`) at frame 883; this is not global coverage. |
| Full Korean pointer draft capacity | SOFT_GATE_PASS | The current Hangul set packs into 48 shared pages, each within the proven 34-code 8x16 pool. |
| Static cloned-page lifecycle | SOFT_GATE_PASS | Small page mapping passes but its native visual gate fails; corrected tier-2 R1-window candidate passes `67/67` mappings with the opening background intact. |
| Bounded full-pointer gameplay progression | PASS_GAMEPLAY_ENTRY_PASS_INTERACTION | Full candidate reached pointer dialogue, restored page state, active combat at frame 915, and interaction pointers 135/136 (`WELCOME` / `WHAT WOULD YOU LIKE`) at frames 1926/1986; finite `lua_done` at frame 7200. Boss defeat/dialogue remains UNKNOWN. |
| Release package | BLOCKED | Requires high-risk families and release checks to pass. |

## Required Before Release

- [ ] Prove menu cursor movement and exit lifecycle with bounded state captures.
- [ ] Audit every other context that shares the cloned R1 page before release.
- [x] Trace and build the Items title/NONE queue owners; the existing action row remains byte-proven on the same route.
- [ ] Audit each other context that shares the R1 raster split.
- [ ] Add context-proven dialogue/UI strings one screen at a time.
- [ ] Check Korean glyph readability on every promoted screen.
- [ ] Run cross-screen boot and gameplay smoke tests without untargeted autoplay.
- [ ] Require manual visual evidence only for release or high-risk candidates.
- [ ] Identify a bounded enemy-clear or boss-spawn route; the interaction/shop route is not boss proof.
- [ ] Promote pointer-dialogue batches only after Japanese context and bounded
  early-boss screen evidence agree with the English structural reference.

## Current Development Candidate Audit

| gate | status | evidence / reason |
| --- | --- | --- |
| Current composed ROM build | PASS | Candidate MD5 `d062b19d23050cd4e148e22fbfff57b7`; IPS round-trip passes. |
| English ownership coverage | SOFT_GATE | 3 full, 7 partial, 89 missing records; missing regions are explicit implementation work, not hidden failures. |
| Main-menu bounded context | PASS | Template and mirror match; Korean source-page tile codes are captured; final R1 remains `0x3E`. |
| Progression bounded context | PASS | `lua_done`; combat starts at frame 915; late event screens are captured. |
| Pointer relocation route | UNKNOWN | Existing probe uses stale fixed-address targets; requires a new relocation-aware route probe. |
| Final release | UNKNOWN | Other renderers, full visual review, boss route, and release checklist remain incomplete. |

Current report: `rom_analysis/full_korean_candidate_smoke_report.md`.

## Full Non-Pointer Candidate Smoke

- [x] Candidate ROM generated deterministically from the current full candidate.
- [x] Two safe equal-length targets applied; 41 unproven targets excluded.
- [x] Bounded FCEUX progression reaches lua_done.
- [x] Entry, combat, and late event-like captures exist.
- [ ] Exact changed-string screen contexts have visual proof.
- [ ] Release promotion approved.

## New Soft-Gate Evidence (2026-08-01)

| gate | status | evidence / reason |
| --- | --- | --- |
| Effective name-table source ownership | SOFT_GATE_PASS_ONE_CONTEXT | 9 differential probes identify only 0x3FB32 as the live owner of PPU sequence 88969F8B; the 0x0561B English static occurrence is inactive on this route. |
| Name-table candidate visual proof | PASS_ONE_CONTEXT | Candidate MD5 df586e888e23761d2da518162444810e; PPU test sequence and frame-1956 screenshot both match. |
| Release promotion of this context | NOT_READY | The candidate uses a bounded test string and covers one renderer context only. |
| Full pointer forced sweep | PASS_SOFT_GATE | 244/244 active rows and 4/4 excluded rows pass bounded forced-render checks; natural event control and boss route remain unproven. |
| Expanded non-pointer build | SOFT_GATE_BUILD_ONLY | 9 equal-length PRG targets plus 18 glyph slots build and round-trip; exact changed-string visual proof is UNKNOWN. |
| Input explorer historical route comparison | UNKNOWN_ROUTE | With KUNIO_EXTRA_DIALOGUE_START=0, the current and expanded candidates reach two unique screens and finite done at frame 1000; this is retained as the historical route comparison. |
## Development Evidence Update (2026-08-01)

The full pointer sweep is a bounded forced-render audit, not a natural gameplay run. It passes 244 active rows and 4 excluded rows. The expanded non-pointer candidate is a build/progression candidate only: its nine equal-length PRG edits still need exact screen-context visual proof.

The input explorer now treats the Lua script's finite done row as a normal completion marker. The historical no-extra-Start route stops after two unique screens, while the default current full candidate reaches four unique screens after the known dialogue transition. The route note is kept separate from the nine non-pointer edits.
| Legacy-route non-pointer candidate | SOFT_GATE_PASS | Candidate MD5 cc450f38b32dfeaa7864b4784874b6ed reaches frame 883 and proves 9/9 selected target records; whole-game release remains blocked. |
| Input explorer default transition | PASS | Default current full candidate reaches four unique screens at frames 121, 361, 655, and 906, then writes finite done at frame 1000. |

## Items Action Candidate Update (2026-08-01)

| gate | status | evidence / reason |
| --- | --- | --- |
| Items action source owner | PASS | English reference chain is proven at ROM 0x13727, CPU $B717, SRAM $6360, and PPU $2363; four fixed-width action slots compile. |
| Items action candidate static build | PASS | Candidate MD5 5dbb442b8bda6efe9039f2e91fd1f88f; IPS round-trip, source scope, and page writes pass. |
| Items action candidate native screen | PASS_RUNTIME | Relative-frame FCEUX capture completed at frame 1906; runtime verifier matches queue PC=B70D, PPU $2363, and MMC3 R1=3E/R6=08/R7=09. GD screenshot is blank, so no visual release claim is made. |
| Items title and NONE rows | PASS_RUNTIME_BYTE_PROOF | PRG/CHR owners are traced; FCEUX frame 1906 proves queue bytes at frame 1737. Native visual is UNKNOWN. |
| Release promotion | NOT_READY | Normal Items R1 page safety and title/empty/action rows are not release-proven. |
## Items Title / NONE Soft Gate (2026-08-01)

- [x] PRG/CHR source owners identified from the English runtime.
- [x] Static source scope and IPS round trip pass.
- [x] Bounded FCEUX route reaches capture frame 1906 without opening-loop autoplay.
- [x] Name, title suffix, and NONE queue bytes pass at frame 1737.
- [x] Existing action queue and PPU bytes remain intact.
- [ ] Native visual proof and shared R0/R1 page audit remain before release.
- [ ] Release promotion remains blocked.
## Pre-Pointer / Name Inventory Gate (2026-08-01)

| gate | status | evidence / reason |
| --- | --- | --- |
| 250-record ownership inventory | PASS | Name-table and pre-pointer records are catalogued separately in rom_analysis/pre_pointer_korean_candidates.csv. |
| Control and glyph safety classification | PASS | 17 control-bearing rows and 33 missing-glyph rows remain blocked; no blind replacement was promoted. |
| Runtime promotion | NOT_READY | Only the separate nine-string legacy-route candidate has bounded 9/9 screen-owner evidence. |
| Release promotion | NOT_READY | Natural progression, visual review, and remaining renderer families are still open. |

## Full Composed Candidate Gate (2026-08-01)

- [x] Compose the English-reference owner chains without overwriting the verified Items name seed.
- [x] Run static scope, IPS round trip, Items byte proof, and composition regression test.
- [x] Confirm bounded input route reaches finite completion and multiple screens.
- [x] Record the overlapping `0x0561A` target as deferred instead of applying a conflicting patch.
- [ ] Native pixel review on a non-transparent screenshot.
- [ ] Natural enemy-clear/boss route proof.
- [ ] Remaining pre-pointer renderer ownership and release-wide shared-page audit.
- [ ] Release promotion.

Realtime AI subtitle overlay is tracked as a parallel usability option, not as ROM release evidence.

## Pre-Pointer High-Code Gate (2026-08-01)

- [x] English reference owner path recorded for PRG Bank 1 and CHR Bank 7.
- [x] Candidate uses English structure composition before Korean data overlay.
- [x] Ten bounded control-free/glyph-complete rows are statically encoded.
- [x] English exact CPU owner probe passes 10/10.
- [x] Korean bounded probe completes with 10/10 exact CPU owners.
- [x] PPU nametable reads are available at the bounded main-menu capture.
- [x] `EN-PRE-138` exact runtime owner is observed at CPU `$9B92`.
- [ ] Row-by-row native pixel attribution and shared-page safety are unresolved.
- [ ] Natural boss progression and release promotion remain blocked.

The high-code candidate remains a development soft-gate artifact and is not a final release ROM.
## Dialogue Ownership Audit Gate (2026-08-01)

- [x] Compare all 250 pre-pointer inventory rows against 722 English dialogue owner runs.
- [x] Keep edge-overlap, oversized, and no-owner rows out of the bounded patch subset.
- [x] Confirm the ten fully contained runtime-mapped rows remain the only promoted high-code subset.
- [ ] Translate and validate the remaining 133 fully contained but unmapped glossary rows.
- [ ] Resolve the 25 edge-overlap and 29 oversized rows without damaging control/separator bytes.
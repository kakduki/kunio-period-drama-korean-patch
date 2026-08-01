# Patched ROM Report

## Historical Opening Candidate

- Status: **PASS_FOR_THREE_OPENING_CONTEXTS**.
- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `46cedd1da6d49643f5dd6bc4895ce706`.
- English reference IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`.
- Pointer 182: `0x05F40` -> `0x071B6` / `$B1A6`, 32 bytes.
- Pointer 183: `0x05F42` moves `$B1CB` -> `0x071D6` / `$B1C6`, 25 bytes.
- Pointer 184: `0x05F44` moves `$B1E0` -> `0x071EF` / `$B1DF`, 23 bytes.
- Pointer 185 remains `$B1F8`; the range guard permits only entries 182-184.
- Changed spans: 129; changed-byte scope audit: PASS; escaped bytes: 0.
- Font profile: `readable` (14 px, BOX resampling, threshold 145), 20 scene-local
  Korean glyphs rendered through paired 8x16 cells.
- Runtime evidence: pointer 182 frame 883 `32/32`; pointer 183 frame 1093
  `25/25`; pointer 184 frame 1399 `23/23`; all bounded runs ended `lua_done`.
- Native visual review: PASS for all three screens.

## Main Menu Candidate

- Isolated menu smoke: **SOFT_GATE_PASS**; cross-screen page-isolation status: **SOFT_GATE_PASS_ISOLATED_R1_POOL**.
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `d425814e4f1249e2872c9eb09f7fb93d`.
- Static menu template: `0x1F2C1`.
- Raster R1 clone switch: `0x3E` -> `0x46` at `0xEE4D`.
- CHR page pair: `0x3E` -> `0x46`.
- Source Bank 7 CHR pages are preserved; Korean tiles exist only in the cloned Bank 8 pair.
- Declared changed spans: `137`.
- Bounded Items probe: **PASS** source-chain proof; current candidate **PASS**.
- Page-isolation result: isolated Korean menu code pool is active without overlapping Items action codes

The generated ROM and IPS remain local build products. This report records the
reproducible candidate identity without placing copyrighted ROM content in Git.
The English patch validates structure only. Pointer 184's Japanese source was
captured from the base ROM before translation. This is not a release-ready full
translation.

## Combined Development Candidate

- Candidate MD5: `6474e2d857dbbcbf1ce8f1e5d8201c08`.
- Combines the three opening records with the scoped main-menu clone-page
  candidate.
- Complete English-guided pointer catalog: `248` rows; Korean work status is
  `development_verified_opening` for 182-184 and `structural_unknown` for the
  remaining records.
- Bounded opening regression on this exact candidate: pointer 182 frame 883
  `32/32`, pointer 183 frame 1093 `25/25`, pointer 184 frame 1399 `23/23`.
- All three opening routes ended with `lua_done`; no combat or unbounded
  autoplay was used.
- Runtime status: `SOFT_GATE_PASS_COMBINED_CANDIDATE`; release verdict remains
`UNKNOWN`.

## First Non-Opening Pointer Batch

- Status: **CANDIDATE_BUILT_RUNTIME_UNKNOWN**.
- Candidate MD5: `863c62ba178973ee1a96cc7971512149`.
- Batch: pointers `2` and `3`, early-boss semantic draft.
- Pointer 2 remains at `$A004`; pointer 3 moves `$A012` -> `$A011` and is
  packed directly after the shorter Korean pointer-2 record.
- Renderer: record-scoped paired 8x16 cells, 15 Korean glyph pairs, controls
  `00/BB/CA/F8/FF` kept explicit.
- Scope audit: `0` escaped changed bytes; candidate IPS and ROM are local and
  ignored by Git.
- Boot regression: **PASS** on the known opening-183 route, frame `1095`,
  `21/21` target reads, terminal reason `lua_done`.
- Boss target probe: **UNKNOWN(route)**. `63` CPU read watchers were registered;
  the known opening route ended at frame `1200` with `target_not_seen`.
- Extended route probe: **UNKNOWN(route)**. The bounded 5000-frame route entered
  phase 3 and produced `266` watched reads, but its screen fingerprint stabilized
  at `8507662:16320`; neither pointer 2 nor 3 matched.
- Runtime report: `rom_analysis/pointer_dialogue_batch_002_003_runtime.md`.
- No visual PASS is claimed for these boss-dialogue records.

## Direct 8x16 Pointer Batch 000-002

- Status: **CANDIDATE_BUILT_RUNTIME_UNKNOWN**.
- Candidate MD5: `ba3ef60856e1d2b5aa4dba40bcf1ff41`.
- Batch: pointers `0`, `1`, and `2`; p1 and p2 are relocated before protected
  pointer 3, while p0 retains its original Bank-1 address.
- Direct source range: `0x81-0x98`, 24 glyphs; helper length: 76 bytes.
- Scope audit: 0 escaped changed bytes. The ROM and IPS are ignored local
  build products; the JSON/Markdown report and font preview are committed.
- Boot smoke: **PASS**, frame `883`, terminal reason `lua_done`.
- Bounded pointer route: **UNKNOWN**, frame `5000`, phase 3, 216 watcher hits,
  final screen fingerprint `8507662:16320`, no complete p0/p1/p2 match.
- Structural risk: p0 contains multiple source messages in the Japanese record;
  this first candidate compacts the Korean draft to one message, so it is not
eligible for release promotion.

## Opening Capacity Tier 2

- Status: **SOFT_GATE_PASS_OPENING_CAPACITY_RUNTIME_AND_VISUAL**.
- Candidate MD5: `6785f321c0fad8d08f4c929aba7c865d`.
- Pointer 182 record: ROM `0x071B6` / CPU `$B1A6`, `37` bytes; helper at
  ROM `0x07FB5`.
- The existing English-derived `0x81-0x9A` pool plus `0xC0-0xC7` was read
  and emitted through the native paired renderer. The bounded frame-883 run
  matched `37/37` source reads and ended with `lua_done`.
- `C0/E0` through `C7/E7` top/bottom tile pairs were observed with mapper
  state `R0=3C, R1=3E`; the native screenshot is recorded in the tier-2
  capture directory.
- This proves a larger opening-context pool, not a whole-game font-page
  strategy. Full draft capacity remains blocked until non-opening contexts
  and mapper/page lifecycle are proven.

The earlier draft audit reported `FULL_DRAFT_CAPACITY_BLOCKED` because one
static page held only 34 source codes. The dynamic multi-page strategy below
supersedes that capacity conclusion while retaining it as historical evidence.

## Full Pointer Korean Development Candidate

- Status: **WHOLE_SCRIPT_RUNTIME_PASS_5_PAGES**.
- Candidate MD5: `7844f2d6f6a67e86e23b2f954d5ebf3c`.
- All 248 pointer rows are represented; 244 rows compile Korean text and four
  excluded non-dialogue rows retain Japanese bytes.
- Packed records occupy ROM `0x05FC4-0x06EB0` end-exclusive (3,820 bytes),
  leaving 336 bytes
  before the loader at `0x07000`.
- Every active record preserves the English reference's non-letter control
  skeleton while replacing its letter/space runs.
- The optimized 48-page plan is compiled into 13 appended CHR banks.
- PTR-181 relocates to `$AACF` and passes the bounded runtime route with
  `$07FF=2B`, `R1=D4`, visible Korean text, and preserved field background.
- Forced pointers 0, 25, 50, 110, and 181 cover five optimized pages; all pass
  page state, R1 mapping, source progression, terminator, Korean text-pixel,
  and field-background checks.
- Pointers 25, 50, and 110 bypass their initial event-dependent `F0` only in
  the visual harness, so this evidence does not promote natural event control.
- Fourteen token-sensitive records use explicit Korean segments around preserved
  English-patch name, item, and status variables instead of proportional splitting.
- Translation QA found no structural failures. Two hundred forty rows have
  direct English-reference review; no translation drafts remain. Forty-seven
  records with dynamic name/item controls are separately flagged for context review.
- IPS apply round trip: PASS.
- Broad runtime and translation review remain required for release.

This candidate resolves the earlier whole-script capacity block at the
development soft gate. It does not retroactively promote every scene to a
visual PASS.

## Static R1 Page Lifecycle

- Small-page candidate: **FAIL_STATIC_R1_VISUAL_BACKGROUND**; MD5
  `7b41d2b1dcd2449d667520ff78c80161`. Its runtime font mapping audit passes
  `28/28`, but the native frame is dialogue-only with a black background.
- Tier-2 static-page candidate: **FAIL**; MD5
  `4246230abe23bbce7abae9affdf5bcdb`. It reaches `37/37` reads and `R1=46`,
  but the runtime target audit fails for the Bank-7 declarations and the
  native capture loses the opening background. Its `C0-C7` capacity is not
  promoted to the cloned page.
- Safe tier-2 static-page candidate: **SOFT_GATE_PASS**; MD5
  `7b7e4ff92c69cc256148a9c5b6fbdfde`. It clones the actual original R1
  `0x800`-byte window to the new R1 window, preserves source Bank 7, reaches
  `37/37` reads, passes `67/67` runtime mappings, and keeps the native opening
  background visible. This proves only the opening-context 17-glyph pool.


## Full-pointer gameplay progression

- Status: **PASS_GAMEPLAY_ENTRY_PASS_INTERACTION_UNKNOWN_BOSS**.
- Candidate MD5: `7844f2d6f6a67e86e23b2f954d5ebf3c`.
- Bounded route: `lua/kunio_stage_progression_probe.lua` with
  `KUNIO_EXTRA_DIALOGUE_START=1`.
- Frame 392 reaches the first full-pointer dialogue with page state `0x2A`.
- Frame 757 records page state `0x00` and normal R1 `0x3E` after the extra
  Start transition.
- Frame 915 enters the combat phase; the bounded route reaches interaction pointers 135/136 (`WELCOME` / `WHAT WOULD YOU LIKE`) at frames 1926/1986; frame 7200 ends with `lua_done`.
- This proves gameplay entry, page recovery, and one non-boss interaction route for the full candidate, not every boss route or release-wide visual approval.

See `rom_analysis/full_pointer_progression_runtime_report.md` for the exact
checkpoint report and raw-output locations.

## Current Full Korean Development Candidate

- Status: **SOFT_GATE_PASS_MENU_AND_GAMEPLAY_ENTRY**.
- Candidate MD5: `d062b19d23050cd4e148e22fbfff57b7`.
- Candidate ROM/IPS: `output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes` and `.ips`.
- The pointer stage compiles 244 active Korean rows and preserves four excluded Japanese rows; the menu stage writes its isolated 16x16 glyphs into the original R1 source page without a global `0x3E -> 0x46` change.
- English ownership audit: 3 fully covered records, 7 partial records, 89 missing records out of 99.
- Menu context: `lua_done`, display/mirror template match, final R1 `0x3E`.
- Progression context: `lua_done`, entry route reaches combat at frame 915 and late event screens after frame 1900.
- Pointer route probe is **UNKNOWN** because its old target address contract predates relocation.
- Release verdict remains **UNKNOWN**. Full visual coverage, other UI renderers, boss route, and release gate evidence are still open.

## Full Non-Pointer Korean Candidate

- Status: SOFT_GATE_PASS for deterministic build and bounded progression smoke.
- Candidate MD5: 18284402f073b91c09d05f52a16b9b9d.
- Composition: full pointer/menu candidate plus two safe equal-length non-pointer PRG edits.
- Applied targets: rom_07227_candidate_84 and watch_rom_0569d_..._7a.
- Excluded targets: 41 candidates remain excluded because they need a padding rule or stronger screen ownership evidence.
- Progression smoke: lua_done; entry captures, combat frame 915, and late event-like frames 1956/2046.
- Exact screen visual proof for the changed non-pointer strings: UNKNOWN.
- Release status: NOT_READY.
- Detailed build report: rom_analysis/full_nonpointer_korean_candidate.md.
- Detailed smoke report: rom_analysis/full_nonpointer_korean_candidate_smoke.md.

## Effective Name-Table Source Probe (2026-08-01)

- Candidate ROM: output/name_table_korean_candidate/kunio_period_drama_korean_name_table_candidate.nes
- Candidate MD5: df586e888e23761d2da518162444810e
- Differential probe scope: 9 ROM occurrences of 88 96 9F 8B.
- Only physical offset 0x3FB32 changed the live natural-route PPU sequence; the English static occurrence at 0x0561B did not.
- Runtime proof: PPU addresses 0x2043-0x2046 changed from 88 96 9F 8B to 81 82 81 82.
- Visual proof: corrected candidate screenshot at frame 1956 shows the test glyphs in the target renderer context.
- Status: SOFT_GATE_PASS_ONE_CONTEXT; the test string is not a release translation and release remains NOT_READY.
## Full Pointer Sweep Audit (2026-08-01)

- Candidate ROM: output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes
- Candidate MD5: d062b19d23050cd4e148e22fbfff57b7
- Scope: 248 bounded forced-pointer runs, one pointer per run, 450 frames each.
- Active rows: 244/244 PASS.
- Excluded non-dialogue rows: 4/4 PASS.
- Source modes: 201 direct terminators, 41 control-stream/static terminators, 2 static terminators not reached by the watch.
- Every run captured text pixels and the preserved field background.
- Final mapper R1 was recorded only as a diagnostic; the page-aware renderer restores the normal mapper state before the final capture, so R1=3E is not a failure.
- Interpretation: whole-script pointer compilation and renderer/page handling pass the development soft gate. This is forced renderer evidence, not natural enemy-clear, boss-spawn, or release-wide visual proof.
- Detailed report: rom_analysis/full_pointer_sweep_runtime.md.
## Expanded Non-Pointer Candidate (2026-08-01)

- Candidate ROM: output/expanded_nonpointer_korean_candidate/kunio_period_drama_korean_expanded_nonpointer_candidate.nes
- Candidate MD5: 12baf49a9b08a0a93b7f2d0e3140289c
- Build: PASS; IPS round trip: PASS.
- Scope: 9 equal-length PRG targets selected from the real frame-883 target record set, plus 18 Korean 8x8 glyph slots copied from the existing font expansion.
- Bounded stage progression: PASS; the route reaches combat and late event-like captures and ends with lua_done.
- Exact changed-string screen proof: UNKNOWN. The current composed candidate route does not reproduce the old frame-883 input-explorer screen.
- Route comparison: both the current composed candidate and the expanded candidate reach only two unique screens in the 1000-frame input explorer run, then write a finite done row. This behavior predates the nine added targets and is not evidence that those targets caused the opening-screen loop.
- Release status: NOT_READY.
- Detailed build report: rom_analysis/expanded_nonpointer_korean_candidate.md.
## Legacy-Route Non-Pointer Candidate (2026-08-01)

- Candidate ROM: output/expanded_nonpointer_legacy_route_candidate/kunio_period_drama_korean_expanded_nonpointer_candidate.nes
- Base ROM MD5: 0d406a85285b4de8468f0dab6aad5fe5
- Candidate MD5: cc450f38b32dfeaa7864b4784874b6ed
- Scope: 9 equal-length PRG targets and 18 Korean 8x8 glyph slots.
- Bounded input route: frame 883 reached on the original English-compatible route.
- Exact target-record proof: 9/9 selected PRG targets have active_expected_match=true at frame 883.
- Capture directory: C:	mplegacy_nonpointer_input_explorer.
- The quarantined 0x07227 Katana target is intentionally not included.
- Soft-gate result: PASS for source ownership and bounded screen capture.
- Release status: NOT_READY; the candidate is a nine-string context build, not a whole-game Korean release.
## Input Explorer Default Transition (2026-08-01)

The current full candidate no longer remains on the second dialogue screen when using the default input explorer route. The known extra Start transition is enabled by default; the bounded run reached four unique screens and ended with a finite done row at frame 1000. Set KUNIO_EXTRA_DIALOGUE_START=0 only for the historical route comparison.

## Items Action Candidate

- Status: BUILT_STATIC_PASS_RUNTIME_PASS.
- Candidate MD5: 5dbb442b8bda6efe9039f2e91fd1f88f.
- Candidate ROM/IPS are local build products and are not committed.
- English-reference source chain: ROM 0x13727 -> PRG bank 4 / MMC3 R7 0x09
  -> CPU $B717-$B737 -> SRAM $6360 -> PPU $2363.
- Four action slots compile as 사용, 버리기, 주기, 버림; source padding and
  queue layout are preserved.
- Static source-chain, changed-scope, font-page, and IPS round-trip checks: PASS.
- Candidate FCEUX capture: PASS; bounded relative-frame route ended lua_done at frame 1909, with action row output at frame 1736.
- Runtime verifier: PASS; candidate source bytes, SRAM queue bytes, PPU $2363 bytes, and Items MMC3 banks all match.
- Native visual proof: UNKNOWN; the generated GD screenshot is transparent blank, so manual visual approval is deferred.
- Title KUNIO'S ITEMS and empty-inventory NONE remain untranslated. This is
  not a final release ROM.
## Items Title / NONE Candidate (2026-08-01)

- Candidate MD5: `fa08179cdbf1198bd7781df0b6c78477`.
- Composition: existing Items action candidate plus PRG `0x0561B`, live CHR/PPU name seed `0x3FB32`, title suffix `0x136F4`, direct-low NONE `0x0FC31`, and eight R0 glyph tiles.
- Bounded FCEUX route: capture frame `1906`; name/title/NONE queue frame `1737`.
- Runtime byte gate: **PASS** for source bytes and queue output; action queue/PPU bytes remain intact.
- Native visual gate: **UNKNOWN** because the available GD screenshot buffer contains transparent pixels.
- Release status: **NOT_READY**.
- Detailed candidate report: `rom_analysis/full_korean_items_title_none_candidate.md`.
- Runtime report: `rom_analysis/items_title_none_runtime.json`.
## Pre-Pointer / Name Inventory (2026-08-01)

The fixed-bank English name/pre-pointer family now has a machine-readable 250-record queue. Exact glossary matches, control-byte skeletons, missing Korean glyphs, and runtime status are reported separately. This is analysis evidence only; no broad replacement was applied. The existing nine-string legacy-route candidate remains the only pre-pointer batch with bounded 9/9 screen-owner evidence.

- Inventory: rom_analysis/pre_pointer_korean_candidates.csv
- Generator: scripts/inventory_pre_pointer_korean_candidates.py
- Release status: NOT_READY.

## Full Composed Development Candidate (2026-08-01)

- Candidate MD5: `5f348772bb6809b1df0e7f84ef2e7603`.
- Composition preserves the English pointer/menu owner chain, direct-low UI, Items action/name/title/NONE chains, and eight non-pointer frame-883-derived records.
- Items runtime byte proof: PASS at frame 1737; bounded capture completes at frame 1906.
- Current input route captures frames 122, 362, 656, 907, and 1147 and finishes at frame 1200.
- `0x0561A` is excluded from this composition because it overlaps the Items name seed at `0x0561B`; the exclusion is recorded, not hidden.
- Native screenshot proof, natural boss route, and release promotion remain UNKNOWN/NOT_READY.
- Detailed report: `rom_analysis/full_korean_composed_candidate.md`.

## Pre-Pointer High-Code Runtime Update (2026-08-01)

- Candidate MD5: `50617961a99d43be949cc28e2ff092a5`.
- English reference exact CPU owner probe: 10/10 at frame 280; bounded run completed at frame 900.
- Korean composed candidate exact CPU owner probe: 10/10 at frame 280; bounded run completed at frame 900, including `EN-PRE-138`.
- Main-menu context capture reached frame 1906 for both runs with PPU nametable reads available.
- Per-row native visual proof and shared Bank 7 page safety remain UNKNOWN; release status remains `NOT_READY`.
- Report: `rom_analysis/pre_pointer_high_runtime.md`.

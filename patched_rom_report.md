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

- Status: **PASS_GAMEPLAY_ENTRY_UNKNOWN_BOSS**.
- Candidate MD5: `7844f2d6f6a67e86e23b2f954d5ebf3c`.
- Bounded route: `lua/kunio_stage_progression_probe.lua` with
  `KUNIO_EXTRA_DIALOGUE_START=1`.
- Frame 392 reaches the first full-pointer dialogue with page state `0x2A`.
- Frame 757 records page state `0x00` and normal R1 `0x3E` after the extra
  Start transition.
- Frame 915 enters the combat phase; 16 screen changes are recorded by frame
  2046; frame 7200 ends with `lua_done`.
- This proves gameplay entry and page recovery for the full candidate, not every
  boss route or release-wide visual approval.

See `rom_analysis/full_pointer_progression_runtime_report.md` for the exact
checkpoint report and raw-output locations.
# Korean Patch Reboot Plan (2026-07-27)

## Goal

Build a playable Korean development candidate from the verified Japanese ROM,
using the English patch as a reverse-engineering reference and using bounded
runtime evidence instead of an unbounded autoplay loop.

The immediate goal is not a release ROM. It is a repeatable pipeline that can
prove one real screen, patch one owned string, and classify the result before
the next screen is attempted.

## English Reference Baseline

The public English reference is the Dynamic Designs Technos Samurai:
Downtown Special v1.00 patch (`TSe-v10.ips`). The repository does not store the
third-party IPS; its verified structure is recorded in:

- `rom_analysis/english_patch_reference.md`
- `rom_analysis/english_patch_implementation_map.md`
- `rom_analysis/english_pointer_map.json`
- `rom_analysis/english_font_slot_map.json`

The useful facts are:

| Area | English reference | Korean consequence |
| --- | --- | --- |
| Main dialogue ownership | 248-entry Bank 1 pointer table at ROM `0x05DD4-0x05FC3` | Relocate records by pointer owner, never by a raw text search alone. |
| Dialogue data | Bank 1 records after the table; 244 pointer entries changed | A Korean record may grow, but every affected pointer and terminator must be tracked. |
| Controls | `0x00`, `0xBB`, `0xCA`, `0xF8`, `0xFF` are separate control/delimiter bytes | Controls stay explicit and cannot be consumed as Hangul codes. |
| English font | Dialogue alphabet uses codes `0x81-0x9A` and physical CHR Bank 7 tiles | This is a renderer/font clue, not permission to replace Bank 7 globally in a partial Korean build. |
| Other text | Name tables, pre-pointer text, UI, item, status, event, and combat regions also changed | Each renderer family needs its own owner, route, font mapping, and regression screen. |

## What The New Evidence Proved

`lua/kunio_stage_progression_probe.lua` keeps the known-good menu entry
sequence through frame 899 and then runs one bounded combat-input pattern. It
does not chain unrelated menu routes and it always emits `summary.tsv` with a
finite completion reason.

Base ROM and the v0.4.2 font-expanded candidate both reached:

- frame 392: field/location dialogue screen;
- frame 1335: active field scene with player and enemies;
- frame 5233: 1P/COM selection screen after the combat route failed to clear the
  encounter;
- frame 7200: `lua_done`, 49 unique screen transitions.

The candidate preserved boot and field entry, but its frame-5233 UI differs
from the base because the partial candidate changed shared CHR font slots.
That is classified as `FONT_SCOPE_FAIL_PARTIAL_GLOBAL_REMAP`, not as a game
boot failure. The candidate is therefore a development probe only and is not
release-ready.

Evidence summary:

- Base ROM: MD5 `0d406a85285b4de8468f0dab6aad5fe5`.
- v0.4.2 candidate: MD5 `ea11dc002a1a7b07682ce00a754b1a61`.
- Base/candidate frame 1335 game pixels match; only the probe overlay row
  differs.
- Base/candidate frame 5233 has a real game-area pixel difference, proving the
  shared-font regression.
- No boss screen or later boss pointer record was reached by this route.

The confirmed PTR-181 probe now proves a real non-opening record at ROM
`0x07198`, PRG Bank 1, CPU `$B188`, through the same parser/emit path as the
opening renderer. A Bank 8 static-page test renders Korean glyphs in that
screen, but its global `R1=46` setup eventually produces a black later screen.
An entry-only page switch also corrupts the target capture. Both are retained
as failure evidence; neither is a release candidate.

A third conditional-mapper candidate resolves that failure for PTR-181. The
renderer sets a scene flag after matching `$B188`; the fixed-bank mapper
wrapper selects the proven `3C/46` page only while screen state `$51=13`, then
clears the flag and returns to `3C/3E`. It renders Korean at frame 392, restores
the original page by frame 622, and completes the 7200-frame route with normal
combat and late-menu screens.

`rom_analysis/full_script_font_capacity.md` quantifies the English-to-Korean
gap. The 144 current translation rows contain 220 unique Hangul syllables.
The runtime-proven paired renderer holds 17 syllables per page, requiring at
least 13 pages by unique count and 23 pages in the current row-packing model.
Even the English patch's entire 181-tile Bank 7 footprint can hold only 45
paired 16x16 syllables per page, requiring at least 5 pages and 9 packed pages.
Therefore the English pointer relocation model is reusable, but its single
alphabet-page assumption is not.

`rom_analysis/pointer_font_page_plan.md` applies the proven 17-syllable page
limit to the full 248-entry pointer-dialogue draft. Of 244 active records, 237
can be assigned without changing their current wording; 7 records individually
exceed the page limit and need shortening or an explicit split. The conservative
sequential plan produces 148 pages. That is an upper-bound implementation plan,
not a proposal to store 148 duplicate fonts: the next optimizer must merge
compatible scene pages and switch only at verified record/scene boundaries.

## Work Order

### Phase 1: Lock ownership and route checkpoints

1. Keep the English-derived 248-row pointer catalog as the ownership map.
2. Keep pre-pointer names, stage labels, menu/status/item text, and pointer
   dialogue in separate renderer families.
3. Use the stage probe's frame-392 field/dialogue and frame-1335 battle scene
   as route checkpoints. A run that stays at the title screen is rejected as a
   launcher/route failure and is not used as patch evidence.
4. Add a named save-state or a confirmed state/warp only when its before/after
   screen and RAM signature are recorded. Do not keep increasing autoplay time
   after a repeated state.

### Phase 2: Prove one non-opening renderer (complete)

1. Capture one stage or boss name on the base ROM with original bytes, CPU
   address, PRG bank, PPU nametable write, and screenshot.
2. Determine whether it uses the English-style Bank 1 dialogue renderer or a
   separate name/location renderer.
3. Build one equal-length Korean glyph test using only slots proven for that
   renderer. PTR-181 now displays the test on a cloned Bank 8 page.
4. Run the same checkpoint route on base and candidate. The target screen
   passes, while the static page lifecycle fails later; this is the current
   boundary, not a release promotion.

### Phase 3: Solve the font scope before script expansion

The failed partial candidate establishes a hard development rule:

- Do not apply a global Bank 7 Korean font replacement while other screens
  still display Japanese text.

Choose one of these implementation paths, with evidence deciding the path:

1. Full-script path: translate enough of the pointer/name/UI script that every
   screen using the remapped tiles is intentionally Korean, and keep the
   required glyph inventory within the proven tile budget. The current full
   translation inventory exceeds one page under both proven and theoretical
   capacity, so this path still needs declared scene/page ownership.
2. Renderer-page path: add a renderer-owned CHR page switch so the Korean page
   is active only while the patched renderer draws, then restore the original
   page for untouched Japanese UI.
3. If neither path is proven, keep the candidate as `UNKNOWN` and do not label
   a partial ROM as a Korean patch.

Current machine-readable inputs for this phase:

- `text_data/pointer_dialogue_korean_draft.tsv`: 248 pointer-owned semantic
  drafts, with four non-dialogue records excluded;
- `rom_analysis/pointer_font_page_plan.json`: deterministic page assignment and
  the seven wording/split blockers;
- `rom_analysis/full_script_font_capacity.json`: independent inventory from the
  existing 144-row translation source.

### Phase 4: Boss route / cheat search

1. Use the video only to identify the intended sequence and scene order.
2. Use the emulator to record actual controller input and state transitions.
3. Search object/enemy state blocks with one bounded write or one paired write,
   taking a screenshot on any state change. A write is a usable route shortcut
   only if it produces the named boss/event screen and remains stable on a
   clean rerun.
4. If no state shortcut is confirmed, use a deterministic combat route with a
   finite frame budget and record `UNKNOWN_ROUTE_STATE`; never treat a title
   screen loop as evidence.

### Phase 5: Candidate and release gates

For every candidate record:

1. static bytes and ownership: PASS/FAIL;
2. boot: PASS/FAIL;
3. route checkpoint: PASS/FAIL/UNKNOWN;
4. target screen context: PASS/FAIL/UNKNOWN;
5. font scope/regression: PASS/FAIL/UNKNOWN;
6. only then include it in a release candidate.

The existing soft-gate artifacts remain the machine-readable output contract:
`build_matrix.md`, `string_candidates.csv`, `false_positive_list.csv`,
`patched_rom_report.md`, `smoke_test_log.txt`, and
`release_gate_checklist.md`.

## Immediate Next Task

Generalize the PTR-181 conditional mapper into a scene-page lookup table, then
compile the next pointer batch with a distinct page identifier. Every added
page must pass its target capture and the same bounded restore/regression
route. The boss route remains a separate bounded investigation until an
enemy-clear or boss-spawn state is confirmed.

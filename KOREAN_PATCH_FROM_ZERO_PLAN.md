# Korean Patch From-Zero Plan

## Current Truth

The project does not have a final Korean patch yet. The current development
candidate proves a bounded renderer and a small set of contexts:

- three opening pointer records have readable 16x16 Korean evidence;
- the main-menu candidate has a scoped font-page change;
- the Items context is protected by a regression capture, but its text is not
  translated;
- combat, event, boss, stage, and later dialogue have not been promoted.

The previous failure mode was a free-running emulator route. It repeatedly
returned to the title/opening state without a named target or a verified state
transition. That route is retired.

## What The English Patch Gives Us

The English patch is a reverse-engineering reference, not Korean source text.
It establishes:

1. a 248-entry Bank 1 pointer table at ROM `0x05DD4`;
2. pointer-owned dialogue records after the table;
3. relocation behavior when translated records grow;
4. dialogue font source slots and the CHR Bank 7 relationship;
5. control bytes that must remain distinct from glyph bytes.

It does not establish Korean wording, Japanese scene meaning, or permission to
copy its code, pixels, header, or binary changes.

The complete structural worklist is now:

- `rom_analysis/pointer_dialogue_catalog.tsv`
- `rom_analysis/pointer_dialogue_catalog.json`
- `rom_analysis/pointer_dialogue_catalog.md`

It contains all 248 pointer rows, including the five rows that were absent from
the earlier conservative catalog.

## Per-Record Contract

Every translated record must have these fields before it can enter a build:

- pointer index and pointer-table ROM offset;
- PRG bank, CPU address, and record ROM offset;
- original Japanese bytes, controls, line breaks, and terminator;
- Japanese meaning from the ROM/transcription/video context;
- Korean text and explicit glyph tokens;
- renderer family and required CHR/font slots;
- shortest deterministic route or a named save/debug/cheat state;
- bounded capture target and evidence file;
- `PASS`, `FAIL`, or `UNKNOWN` with a classified reason.

An English reference row alone is never enough to patch a Korean record.

## Work Order

### Phase 0: Inventory

1. Keep the 248-row pointer map as the source of ownership.
2. Keep pre-pointer name/menu/status/item blocks separate from pointer dialogue.
3. Maintain `false_positive_list.csv` for bytes that resemble text but lack a
   renderer owner or screen context.

### Phase 1: Renderer Families

1. Retain the verified opening 16x16 paired-cell renderer as a local baseline.
2. Map the original Japanese dialogue tile path before adding more syllables.
3. Build a larger font allocation only from concrete scene needs.
4. Treat menu, status, item/shop, name-table, and pointer dialogue as separate
   families until each has its own runtime evidence.

### Phase 2: Reachable Contexts

1. Use short menu routes for title/menu and Items.
2. Use targeted state or debug memory for stage/status and item screens.
3. Use a verified save/debug/cheat state for boss/event dialogue. The state is
   a way to reach a screen, not a substitute for screen evidence.
4. Never use combat autoplay to discover dialogue locations.

### Phase 3: Candidate Batches

1. Select one context-confirmed record or a very small same-family batch.
2. Encode Korean text with an explicit token catalog.
3. Relocate only declared records and update only their owned pointers.
4. Build an ignored local ROM plus a committed byte-scope/report manifest.

### Phase 4: Bounded Verification

Each run must declare a ROM, route, hard frame budget, target bytes, capture
frame/condition, and terminal reason. Stop on the first target capture. A run
that shows only the title screen is `UNKNOWN(route)`, not a successful patch.

### Phase 5: Promotion

Development uses soft gates so useful candidates can be produced while visual
evidence is pending. Only records with scoped bytes, correct boot, correct
target reads, and readable native output enter a release candidate.

## Immediate Next Targets

1. Use the complete catalog to choose the first non-opening record with a
   recoverable route and a known Japanese context.
2. Extend the fixed opening regression route so it proves the combined
   development candidate without returning to blind autoplay.
3. Resolve one separate renderer family, starting with a direct menu/item
   context before attempting combat dialogue.
4. Build boss/event work only after a reusable targeted state exists.

## Release Gate

Release remains blocked until the final build has a base-ROM identity check,
complete changed-byte audit, bounded boot evidence, all required renderer
families covered, no unresolved high-risk false positives, and native visual
proof for high-risk text. The current candidate is development-only.

# Korean Patch Reboot Plan

## Goal

Build a maintainable Korean patch for the Japanese ROM without treating the
opening scene as a search loop. The current three-record opening candidate is
a regression baseline, not the route used to discover future text.

## Current Baseline

- Base ROM: MD5 `0d406a85285b4de8468f0dab6aad5fe5`.
- Three opening dialogue contexts are verified in FCEUX with readable 16x16
  Korean: pointer 182 (`32/32` reads), pointer 183 (`25/25`), and pointer 184
  (`23/23`). See
  `rom_analysis/opening_ptr_182_184_16x16_readability_runtime.md`.
- The candidate is deliberately scene-local. It proves a renderer path and a
  small Korean glyph set; it is not a full translation or a release build.

## Non-Negotiable Rules

1. Never use unbounded autoplay to find dialogue.
2. Every FCEUX run must declare a target, hard frame budget, deterministic
   inputs, capture condition, and terminal reason.
3. A byte sequence is not translated merely because it resembles text. It
   needs a renderer family, ROM owner, controls/terminator, and screen context.
4. Generated ROMs and IPS files remain local and ignored. Git contains the
   compiler, catalogs, reports, tests, and small visual evidence.
5. A static build may be useful, but it remains `UNKNOWN` until its named
   screen is captured. A missing manual dump never blocks candidate generation.

## English Patch Boundary

The English IPS is a structural reference only. It may establish:

- pointer-table ownership and record relocation rules;
- dialogue source-byte and CHR slot relationships;
- which ROM blocks are likely text, code, fonts, or unrelated data.

It may not supply Korean wording, English pixels, English code, header edits,
or broad binary changes for the Korean patch. Japanese base-ROM evidence,
Japanese transcriptions, and video timing establish meaning and order.

## Repeatable Per-Family Loop

1. **Map**: classify one renderer family and create a catalog row with pointer
   or ROM offset, PRG bank, original bytes, controls, and owner.
2. **Reach**: prepare the shortest deterministic route. Use direct menu input,
   save/debug state, or a verified cheat state for events and bosses; do not
   attempt to play combat automatically.
3. **Interpret**: capture the Japanese base context, then write compact Korean
   text and identify the exact glyph additions it requires.
4. **Build**: compile a candidate with a changed-byte allowlist covering only
   declared records, pointers, helper code, and CHR tiles.
5. **Smoke**: run the target route once. Capture the screen and stop as soon
   as the expected bytes are read.
6. **Classify**: record `PASS`, `FAIL`, or `UNKNOWN` with the reason. A failure
   must name its class: boot, pointer, renderer, font, context, or route.
7. **Promote**: add only passing records to the next scene batch. Keep all
   other rows out of a release build.

## Work Order

1. Keep the verified three-opening candidate as the fixed regression test.
2. Inventory title/menu strings and choose one that a short menu-navigation
   script can reach from boot.
3. Treat status labels as a separate renderer family and use an explicit menu
   route or state, not gameplay progression.
4. Treat item/shop text as another separate family with its own state/route.
5. For event and boss dialogue, first create a reproducible save/debug/cheat
   state. The state is for reaching a target screen, not for bypassing evidence.
6. Expand the Korean font only when a concrete next context needs it and that
   context can be captured. Do not reserve a global glyph pool by guesswork.

## Release Gate

Development uses soft gates: a built candidate may exist with `UNKNOWN` visual
status. Release promotion requires base-ROM identity, scoped-byte audit,
bounded boot/target evidence, native readability evidence for high-risk text,
and all required renderer families marked `PASS`.

# Korean Patch Execution Plan

## Purpose

Build a maintainable Korean patch for `Kunio Kun no Jidaigeki Dayo Zenin
Shuugou! (J)` without relying on blind gameplay. The working reference is the
public English patch's *structure*, not its English wording or its binary
changes.

The first Korean opening-dialogue proof is retained as evidence that the
dialogue path and Bank 7 font slots can be changed. It is not a release
candidate: its 8x8 rasterized Korean font fails the release readability gate.

## Non-Negotiable Rules

1. Do not run unbounded FCEUX autoplay. A capture script must have a target,
   a frame limit, and an explicit stop condition.
2. Do not patch every string-looking byte sequence. A candidate must have a
   known context, encoding, terminator, and ROM ownership.
3. Do not copy English text, code, or header changes into the Korean patch
   merely because the English patch uses them.
4. Do not scale script translation until the Korean font path passes a real
   in-game readability check.
5. Every generated ROM/IPS stays local and ignored. Git contains scripts,
   metadata, text reports, and small visual evidence only.

## Reference Model

The English patch establishes these facts for the primary dialogue path:

- A 248-entry pointer table starts at ROM `0x05DD4`.
- English dialogue uses byte codes `0x81-0x9A` for `A-Z`.
- Those codes resolve to physical CHR Bank 7 tiles `0x181-0x19A`.
- The primary dialogue records live in PRG Bank 1 and use control bytes and
  pointer relocation separately from their glyph bytes.

This gives the Korean patch a safe way to identify text records, font slots,
and pointer ownership. It does not prove that every other text surface uses
the same renderer.

## Work Streams

### A. Renderer and Font First

Goal: choose a Korean rendering method that remains legible in the actual
dialogue window.

1. Preserve the existing 8x8 proof as a baseline only.
2. Build and compare dedicated Korean bitmap candidates at native size; do not
   judge a font from an enlarged preview alone.
3. Capture the same opening dialogue scene for every candidate with the
   bounded input route.
4. Apply the readability gate to the native screenshot:
   - individual syllables remain distinguishable;
   - common words can be read without relying on the source text;
   - punctuation, spaces, and speaker labels remain clear;
   - no glyph collides with a neighbour or is confused with another glyph.
5. Use the game's existing vertical two-tile dialogue layout as an 8x16
   technical building block. If the native capture remains too narrow for
   Korean reading, pair two adjacent 8x16 cells into one 16x16 syllable before
   considering any new VRAM queue format.

Deliverables:

- `rom_analysis/font_readability_gate.md`
- native-size comparison screenshots
- a deterministic Korean tile-font generator and tests

### B. Script Catalog and Translation Source

Goal: create a conservative catalog before translation.

1. Pair each base-ROM pointer record with its English-reference pointer index.
2. Preserve Japanese bytes and all control tokens exactly.
3. Use Japanese transcriptions and video timing only to resolve the Japanese
   meaning and scene order.
4. Translate by scene/context, beginning with the opening and one menu or
   item surface. Do not use the English patch as a source translation.
5. Mark every row as `confirmed`, `needs-context`, or `excluded`.

Catalog fields:

`id`, `context`, `pointer_offset`, `jp_offset`, `jp_bytes`, `jp_text`,
`en_reference`, `control_tokens`, `width`, `korean_text`, `status`.

### C. Compiler and Packing

Goal: make text edits reproducible and bounded.

1. Encode Korean text through the approved font map only.
2. Preserve line breaks, speaker markers, pauses, waits, and terminators as
   explicit tokens.
3. Recalculate pointers only for records that grow or move.
4. Enforce changed-byte allowlists covering text records, their pointer bytes,
   and approved CHR tiles.
5. Add round-trip tests so an unmodified extracted record rebuilds byte-for-byte.
6. Do not treat a per-batch glyph allocation as a release-capable font system.
   Establish and verify the larger dialogue-code/CHR pool before a multi-scene
   Korean build is promoted.

### D. Context-by-Context Verification

Use one short, deterministic verification case per renderer family:

| Order | Surface | Verification method |
| --- | --- | --- |
| 1 | opening dialogue | bounded scripted route and target read/capture |
| 2 | title/menu | short menu navigation script |
| 3 | status labels | targeted menu route or saved state |
| 4 | item/shop text | targeted state/route |
| 5 | event and boss dialogue | save state, debug state, or a verified cheat route |

A result is recorded as:

- `PASS`: ROM scope, boot, target record, and native visual output match.
- `FAIL`: a concrete fault is known, such as font collision, wrong pointer,
  boot failure, or context mismatch.
- `UNKNOWN`: static checks pass but no target-screen evidence exists.

### E. Incremental Release Assembly

1. Translate and test a small scene batch.
2. Rebuild ROM/IPS locally and run smoke tests.
3. Promote only passing rows into the next batch.
4. Produce a ROM-free release only after all high-risk renderer families and
   pointer changes have evidence.

## Immediate Sequence

1. Record the 8x8 font as a functional-display pass but a readability failure.
2. Keep the 8x16 vertical pair as a verified renderer building block, not the
   final Korean font decision.
3. Use paired 8x16 cells for a 16x16 Korean syllable and prove it on one real
   opening record with the bounded frame-883 route.
4. Solve release-capable glyph capacity and paired-cell width accounting before
   expanding translation text.
5. Expand the opening catalog only from context-checked Japanese material, then
   build and capture one complete record at a time.

## Current Checkpoint

The following proof-level work is complete:

- The English IPS was used in memory only to map the 248-entry pointer table
  and the `0x81-0x9A` dialogue font slots. No English ROM or IPS is stored.
- Pointer entry 182 is tied to ROM `0x071B6`, CPU `$B1A6`, and a real opening
  dialogue capture at frame 883.
- The existing two vertical dialogue tiles render one source byte as an 8x16
  cell. That path booted and read the expected 37 bytes, but its native
  screenshot is too narrow for the intended Korean readability bar.
- Two adjacent 8x16 cells now render one Korean syllable as 16x16. The paired
  one-record candidate booted, matched all 37 runtime record reads, captured
  the native scene at frame 883, and passed the one-record font review.
- `text_data/korean_scene_batches/opening_ptr_182_16x16.json` records the
  compact eight-glyph font proof explicitly. Its wording is not a release
  translation and must not be promoted as one.
- `text_data/korean_scene_batches/opening_ptr_182.json` is compiled with
  explicit glyph/control tokens. Its compiler reproduces the verified record
  byte-for-byte and rejects a batch that exceeds the current safe slot pool.

The following is deliberately still open:

- The paired 16x16 proof uses eight unique Korean glyphs and 16 source slots.
  It is not evidence that every dialogue record can share one final Korean
  font page.
- The current proven pool contains 17 one-cell codes (`0x81-0x89`,
  `0x8C-0x93`) and excludes `0x8A` and `0x8B`. A 16x16 syllable consumes two
  of those codes, so the proof pool supports only eight complete syllables and
  one spare code; it does not authorise broad translation or untested CHR slots.
- Pointer relocation, menu renderers, status labels, and event/boss dialogue
  remain separate context families and must not inherit this result blindly.

## Next Technical Gate

1. Audit candidate source/CHR slots and determine whether a larger static pool
   or scene-local CHR paging can support a release-capable 16x16 glyph set.
2. Record each validated source and four-tile glyph placement in
   `rom_analysis/dialogue_glyph_capacity_plan.md`; do not extend allocation
   based only on byte similarity.
3. Add paired-cell width accounting and explicit control-token preservation to
   the scene compiler before encoding a full opening record.
4. Capture each expanded record through a bounded, known context route and
   solve the multi-scene capacity strategy before bulk translation or pointer
   relocation.

## What Is Deliberately Retired

- Long-running opening-screen captures used to infer text locations.
- Broad scans that assign meaning to unconfirmed byte runs.
- Treating legacy v0.4.x candidates as the current release line.
- Calling a font ready merely because Korean pixels appeared on screen.

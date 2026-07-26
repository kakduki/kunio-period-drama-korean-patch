# Korean Patch Execution Plan

## Purpose

Build a maintainable Korean patch for `Kunio Kun no Jidaigeki Dayo Zenin
Shuugou! (J)` without relying on blind gameplay. The working reference is the
public English patch's *structure*, not its English wording or its binary
changes.

The first Korean opening-dialogue proof is retained as evidence that the
dialogue path and Bank 7 font slots can be changed. Its 8x8 raster is a failed
readability baseline; the current opening direction is paired 16x16 Korean.

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
  and the `0x81-0x9A` dialogue font slots, and to confirm that this dialogue
  family can relocate records. No English ROM or IPS is stored.
- Pointer entry 182 is tied to ROM `0x071B6`, CPU `$B1A6`, and a real opening
  dialogue capture at frame 883.
- The existing two vertical dialogue tiles render one source byte as an 8x16
  cell. That path booted and read the expected 37 bytes, but its native
  screenshot is too narrow for the intended Korean readability bar.
- Two adjacent 8x16 cells now render one Korean syllable as 16x16. The paired
  candidates booted, matched their target reads, captured the native scene at
  frame 883, and passed the opening readability review.
- The fixed opening route proved 17 distinct Korean syllables through source
  slots `0x81-0x9A` and `0xC0-0xC7`. The latter slots have this route's runtime
  evidence only; they are not a blanket Bank 7 allocation.
- `text_data/korean_scene_batches/opening_ptr_182_16x16_relocation_proof.json`
  encodes a context-checked 45-byte opening record with explicit control bytes.
  It renders `쿠니마사 어서 움직여!` and `분조 두목이 큰일이야!` at frame 883.
- That 45-byte record overlaps pointer 183's base record. The builder copies
  the exact 21-byte neighbour from ROM `0x071DB` to the approved cave tail at
  `0x07FF6` / `$BFE6`, changes only pointer-table entry 183, and checks all
  changed bytes against its allowlist. The primary record has `45/45` matching
  runtime reads and `lua_done`; pointer 183's own displayed context remains
  `UNKNOWN`.

The following is deliberately still open:

- The 17-syllable paired pool is still scene-local. It cannot support the full
  Korean script without a wider, separately verified allocation strategy.
- The helper range used for `0x81-0x9A` plus `0xC0-0xC7` deliberately excludes
  the renderer-special `0xBB` speaker separator. Speaker formatting therefore
  needs its own helper design and capture.
- Pointer relocation beyond the one audited neighbour, menu renderers, status
  labels, and event/boss dialogue remain separate context families and must not
  inherit this result blindly.

## Next Technical Gate

1. Design a dialogue helper that can preserve `0xBB` speaker formatting while
   keeping the proven Korean source ranges, then validate it on one record.
2. Audit a larger static pool or a scene-local CHR paging method for a
   release-capable 16x16 glyph set; record every source and four-tile placement
   in `rom_analysis/dialogue_glyph_capacity_plan.md`.
3. Generalize pointer growth only through a catalog-declared allocation and a
   static owner scan, then capture every relocated record in its own context.
4. Move to title/menu, item/status, and event/boss text only through short,
   deterministic routes, save states, or debug states. Never revive unbounded
   opening-screen autoplay as a discovery method.

## What Is Deliberately Retired

- Long-running opening-screen captures used to infer text locations.
- Broad scans that assign meaning to unconfirmed byte runs.
- Treating legacy v0.4.x candidates as the current release line.
- Calling a font ready merely because Korean pixels appeared on screen.

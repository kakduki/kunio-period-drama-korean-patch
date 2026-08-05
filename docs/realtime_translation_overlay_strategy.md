# Real-Time Translation Overlay Strategy

Date: 2026-08-05

## Decision

Build a real-time Korean translation overlay as a parallel development path.
It is the fastest way to make the Japanese ROM playable in Korean while the
native ROM patch continues toward release quality.

The overlay is not a replacement for the patch. It avoids ROM-space and
pointer-table risk, but it cannot provide native Korean pixels, portable
patch distribution, or a final visual proof inside the ROM.

## Recommended Architecture

1. FCEUX Lua observes the text buffer, nametable, or known pointer reads.
2. The Lua script emits a small JSON event containing the source text,
   pointer/context when known, and the frame number.
3. A local Windows overlay renders the Korean line above the emulator window.
4. A glossary/cache is checked first; an AI translation request is used only
   for an uncached Japanese line.
5. The accepted Korean result is written back to `translation/realtime_overlay.csv` as
   a reviewable draft, never directly into a release ROM.

Screenshot OCR is a fallback only. NES text is small and tile-based, so the
preferred source is the emulator's decoded bytes or text buffer. OCR can be
used for screens whose memory ownership has not yet been identified.

## What The English Reference Gives Us

`tools/reference/TSe-v10.ips` is valuable as a structural reference. It helps
locate changed text/font regions and shows how the original game allocates
space and redirects pointers. It does not automatically provide a Korean
script, Korean glyphs, line wrapping, or proof that every dialogue record uses
the same renderer.

The Korean path still needs to verify:

- text record and pointer ownership;
- PRG bank and available ROM space;
- Korean tile/font coverage and line width;
- menu, item, battle, map, and dialogue renderers separately;
- boot, bounded runtime, and native-pixel evidence.

## Current Evidence

- The base ROM and English reference are identified and reproducible.
- Three opening dialogue records have bounded runtime/source-read and visual
  proof.
- The selected-only manifest candidate builds and boots in a bounded FCEUX
  process check.
- The full candidate is still `NOT_READY`; natural combat/boss routing and
  full native-pixel coverage remain `UNKNOWN`.

The current status is recorded in `rom_analysis/manifest_build_gate.md` and
`docs/project-status.md`.

## Delivery Order

### Overlay MVP

- Add a bounded FCEUX Lua event emitter for the proven opening records.
- Add a local overlay receiver with a manual/glossary translation cache.
- Add AI translation only for cache misses, with a visible `UNCHECKED` state.
- Log source text, context, translation, latency, and acceptance status.

### Native Patch

- Promote only rows with a proven pointer/renderer owner.
- Use overlay-captured lines to populate reviewed translation drafts.
- Generate one-record or small-batch candidates and run the existing smoke
  checks.
- Require native visual proof only for release candidates or high-risk rows.

## Stop Conditions

- Do not run unbounded autoplay or leave an emulator looping on the opening.
- Do not patch a byte based only on an OCR match or a guessed RAM address.
- Do not treat an overlay translation as evidence that the ROM patch is safe.
- Do not call the native patch complete until the release gate is green.

## MVP Status

The first end-to-end MVP is now verified for the reached `OPENING-182` and
`OPENING-183` records. A bounded run on the base ROM emitted three events at
frames 656, 718, and 1047; the Python receiver resolved the latest Korean
translation with status `CACHED`. `OPENING-184` was registered but not reached
before the frame cap. Evidence is recorded in
`rom_analysis/realtime_overlay_mvp.md`.

## Latest Bounded Evidence

The corrected overlay target table now covers four opening records. A 1,900-frame
run emitted `OPENING-182` at frame 656, `OPENING-183` at 718 and 1047,
`OPENING-184` at 1349, and `OPENING-185` at 1655. All four IDs have cache rows;
the latest p185 event resolves as `CACHED`. This remains a sidecar development
proof, not native ROM release evidence.

## Updated Evidence (2026-08-06)

The sidecar target table now covers six verified records: p182-p185 and
p194-p195. A bounded 5,000-frame run registered 158 source-read bytes and
finished with a Lua lua_done row. It emitted p194 at frames 1671 and 4517
and p195 at frame 4857; both resolved from the reviewed Korean cache.

The wrapper also reported a timeout while waiting for FCEUX to exit. Because
the copied summary contains lua_done at frame 5000, this is classified as a
launcher-exit timeout rather than an unbounded emulator run.

p196-p197 remain excluded from the overlay target table until their source
record and renderer context are proven. The sidecar result is still not
native ROM release evidence.
## Review Log

The receiver writes each newly displayed event to
rom_analysis/realtime_overlay/drafts.tsv by default. Each row retains the
frame, event ID, context, expected source bytes, record snapshot, displayed
translation, status, latency, and acceptance classification.

Cached reviewed rows use reviewed_cache. Optional translator-command results
use AI_UNCHECKED and pending_review. Unresolved events use UNCHECKED and
unresolved. None of these rows is inserted into the native ROM automatically.
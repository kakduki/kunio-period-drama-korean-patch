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
5. The accepted Korean result is written back to `translation/script.csv` as
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

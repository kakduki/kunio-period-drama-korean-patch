# Korean Patch Work Plan

## Current Result

The project now has one bounded, native proof of readable Korean dialogue:

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- English reference IPS SHA-256:
  `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`.
- Opening pointer 182: ROM `0x071B6`, PRG Bank 1, CPU `$B1A6`.
- Candidate record: 38 bytes, one-byte growth, with pointer 183 preserved at
  the approved code-cave tail.
- Native FCEUX frame 883: bounded completion, 38/38 target reads, screenshot,
  and visual readability all pass.

This is a development proof, not a release build and not evidence that every
screen uses the same text renderer.

## What Stops Here

Do not use unbounded autoplay to search for later dialogue. In particular, do
not loop the opening route after this point. It is only a deterministic
regression case for pointer 182.

Do not translate all extracted byte strings. A string becomes patchable only
after its renderer family, control bytes, ROM ownership, and screen context
are recorded.

## English Patch Reference

The public English patch is a structural reference only:

1. It proves a 248-entry dialogue pointer table at `0x05DD4-0x05FC3`.
2. It proves dialogue source slots `0x81-0x9A` map to CHR Bank 7 tiles
   `0x181-0x19A`.
3. It proves Bank 1 dialogue records can be relocated with pointer updates.
4. Its English wording, header change, and unrelated renderer changes are not
   copied into the Korean patch.

## Build Order

1. Maintain a context catalog before translating:
   pointer, ROM offset, PRG bank, original bytes, control tokens, Japanese
   context, Korean wording, glyphs, and verification status.
2. Treat each renderer family independently:
   dialogue, title/menu, status labels, item/shop text, and event/boss text.
3. For a single confirmed record, build a scoped candidate ROM with an
   allowlist that covers only text, declared pointers, helper code, and CHR
   tiles.
4. Run a bounded smoke test that has a named target, a hard frame limit, and a
   capture/stop condition.
5. Record results as PASS, FAIL, or UNKNOWN. A static build without a target
   screen stays UNKNOWN rather than being discarded or promoted.

## Next Work

1. Use the existing English pointer map and Japanese catalog to choose a
   second record whose scene can be reached by a short deterministic menu
   route, save state, debug state, or verified cheat route.
2. Create a target-specific Lua script before launching FCEUX. It must never
   depend on free-form combat or boss progression.
3. Extend Korean glyph capacity only after the exact new screen proves its CHR
   mapping. Do not reuse the opening's scene-local allocation blindly.
4. Verify pointer 183 separately before relying on its relocation in a broader
   batch.
5. Promote only context-level passes into a release candidate; require manual
   visual evidence for high-risk release rows, not for every exploratory
   static build.

## Evidence

- English structure: `rom_analysis/english_patch_implementation_map.md`
- Font decision: `rom_analysis/font_readability_gate.md`
- Readability comparison: `rom_analysis/opening_font_profile_comparison/report.md`
- Native proof:
  `rom_analysis/opening_dialogue_16x16_readability_proof_capture/analysis.md`

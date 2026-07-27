# Release Gate Checklist

Current release verdict: **UNKNOWN**

| gate | status | evidence / reason |
| --- | --- | --- |
| Base ROM identity | PASS | MD5 matches the verified Japanese base. |
| English structural reference | PASS | Recorded IPS SHA-256; used only for structure. |
| Scoped three-record opening build | PASS | 129 declared changed spans; 0 escaped bytes; range guard protects pointer 185. |
| Bounded boot and target reads | PASS | 182 frame 883 `32/32`; 183 frame 1093 `25/25`; 184 frame 1399 `23/23`; all `lua_done`. |
| Complete pointer ownership catalog | PASS | English-guided Bank 1 catalog contains all 248 pointer rows; five missing conservative rows are explicitly listed for investigation. |
| Native Korean readability | PASS | Three native 16x16 opening screenshots reviewed. |
| Japanese source context | PASS | Pointer 184 base-ROM capture is recorded; prior opening records already had context evidence. |
| Scoped main-menu build | SOFT_GATE_PASS_ISOLATED_R1_POOL | Menu capture and the bounded Items page-isolation smoke both pass. |
| Items shared-page probe | PASS | ROM -> CPU -> SRAM -> PPU chain is proven; current Korean pool does not overlap the action codes. |
| Menu cursor lifecycle | UNKNOWN | A post-template probe was inconclusive. |
| Other R1 raster contexts | UNKNOWN | Shared split needs per-screen audit. |
| Release-wide Korean glyph capacity | UNKNOWN | Current allocations remain context-scoped. |
| Full translated script | NOT_STARTED | Deliberately blocked until renderer-family evidence exists. |
| Non-opening pointer batch | UNKNOWN | Pointers 2-3 compile and relocate safely; the bounded opening/extended routes reached no target capture, so early-boss screen context is not yet captured. |
| Direct 8x16 pointer batch | UNKNOWN | Pointers 0-2 compile with 24 glyphs and 0 escaped bytes; boot passes at frame 883, but the frame-5000 route has no complete target match and p0 has a multi-message structural risk. |
| Opening-context Korean glyph capacity | SOFT_GATE_PASS | Pointer 182 proves 34 paired source slots (`0x81-0x9A` plus `0xC0-0xC7`) at frame 883; this is not global coverage. |
| Full Korean pointer draft capacity | BLOCKED | 244 active rows require 378 unique non-space symbols while only 34 direct source slots are proven in one opening context. |
| Static cloned-page lifecycle | SOFT_GATE_PASS | Small 7-glyph page candidate keeps the opening scene and passes `28/28` runtime tile mappings; tier-2 `C0-C7` page candidate remains FAIL. |
| Release package | BLOCKED | Requires high-risk families and release checks to pass. |

## Required Before Release

- [ ] Prove menu cursor movement and exit lifecycle with bounded state captures.
- [ ] Audit every other context that shares the cloned R1 page before release.
- [ ] Build an Items-specific second PPU queue row before writing 16x16 Korean action text.
- [ ] Audit each other context that shares the R1 raster split.
- [ ] Add context-proven dialogue/UI strings one screen at a time.
- [ ] Check Korean glyph readability on every promoted screen.
- [ ] Run cross-screen boot and gameplay smoke tests without untargeted autoplay.
- [ ] Require manual visual evidence only for release or high-risk candidates.
- [ ] Promote pointer-dialogue batches only after Japanese context and bounded
  early-boss screen evidence agree with the English structural reference.

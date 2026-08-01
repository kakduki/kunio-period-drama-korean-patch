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
| Release-wide Korean glyph capacity | SOFT_GATE_PASS | The optimized 48-page build fits 13 appended CHR banks; forced pointers 0/25/50/110/181 prove pages 10/14/39/30/41 with matching state/R1 and preserved backgrounds. Natural event control and broad scene auditing remain open. |
| Full translated script | CANDIDATE_BUILT | 244 Korean rows compile with preserved English non-letter control skeletons; 14 token-sensitive rows use explicit Korean segments, 244 rows are English-reference reviewed, no translation drafts remain, and four excluded rows retain Japanese bytes. |
| Non-opening pointer batch | UNKNOWN | Pointers 2-3 compile and relocate safely; the bounded opening/extended routes reached no target capture, so early-boss screen context is not yet captured. |
| Direct 8x16 pointer batch | UNKNOWN | Pointers 0-2 compile with 24 glyphs and 0 escaped bytes; boot passes at frame 883, but the frame-5000 route has no complete target match and p0 has a multi-message structural risk. |
| Opening-context Korean glyph capacity | SOFT_GATE_PASS | Pointer 182 proves 34 paired source slots (`0x81-0x9A` plus `0xC0-0xC7`) at frame 883; this is not global coverage. |
| Full Korean pointer draft capacity | SOFT_GATE_PASS | The current Hangul set packs into 48 shared pages, each within the proven 34-code 8x16 pool. |
| Static cloned-page lifecycle | SOFT_GATE_PASS | Small page mapping passes but its native visual gate fails; corrected tier-2 R1-window candidate passes `67/67` mappings with the opening background intact. |
| Bounded full-pointer gameplay progression | PASS_GAMEPLAY_ENTRY_PASS_INTERACTION | Full candidate reached pointer dialogue, restored page state, active combat at frame 915, and interaction pointers 135/136 (`WELCOME` / `WHAT WOULD YOU LIKE`) at frames 1926/1986; finite `lua_done` at frame 7200. Boss defeat/dialogue remains UNKNOWN. |
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
- [ ] Identify a bounded enemy-clear or boss-spawn route; the interaction/shop route is not boss proof.
- [ ] Promote pointer-dialogue batches only after Japanese context and bounded
  early-boss screen evidence agree with the English structural reference.

## Current Development Candidate Audit

| gate | status | evidence / reason |
| --- | --- | --- |
| Current composed ROM build | PASS | Candidate MD5 `d062b19d23050cd4e148e22fbfff57b7`; IPS round-trip passes. |
| English ownership coverage | SOFT_GATE | 3 full, 7 partial, 89 missing records; missing regions are explicit implementation work, not hidden failures. |
| Main-menu bounded context | PASS | Template and mirror match; Korean source-page tile codes are captured; final R1 remains `0x3E`. |
| Progression bounded context | PASS | `lua_done`; combat starts at frame 915; late event screens are captured. |
| Pointer relocation route | UNKNOWN | Existing probe uses stale fixed-address targets; requires a new relocation-aware route probe. |
| Final release | UNKNOWN | Other renderers, full visual review, boss route, and release checklist remain incomplete. |

Current report: `rom_analysis/full_korean_candidate_smoke_report.md`.

## Full Non-Pointer Candidate Smoke

- [x] Candidate ROM generated deterministically from the current full candidate.
- [x] Two safe equal-length targets applied; 41 unproven targets excluded.
- [x] Bounded FCEUX progression reaches lua_done.
- [x] Entry, combat, and late event-like captures exist.
- [ ] Exact changed-string screen contexts have visual proof.
- [ ] Release promotion approved.

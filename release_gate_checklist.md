# Release Gate Checklist

Current release verdict: **UNKNOWN**

| gate | status | evidence / reason |
| --- | --- | --- |
| Base ROM identity | PASS | MD5 matches the verified Japanese base. |
| English structural reference | PASS | Recorded IPS SHA-256; used only for structure. |
| Scoped three-record opening build | PASS | 129 declared changed spans; 0 escaped bytes; range guard protects pointer 185. |
| Bounded boot and target reads | PASS | 182 frame 883 `32/32`; 183 frame 1093 `25/25`; 184 frame 1399 `23/23`; all `lua_done`. |
| Native Korean readability | PASS | Three native 16x16 opening screenshots reviewed. |
| Japanese source context | PASS | Pointer 184 base-ROM capture is recorded; prior opening records already had context evidence. |
| Scoped main-menu build | SOFT_GATE_PASS | One real menu template and clone-page capture passed. |
| Menu cursor lifecycle | UNKNOWN | A post-template probe was inconclusive. |
| Other R1 raster contexts | UNKNOWN | Shared split needs per-screen audit. |
| Release-wide Korean glyph capacity | UNKNOWN | Current allocations remain context-scoped. |
| Full translated script | NOT_STARTED | Deliberately blocked until renderer-family evidence exists. |
| Release package | BLOCKED | Requires high-risk families and release checks to pass. |

## Required Before Release

- [ ] Prove menu cursor movement and exit lifecycle with bounded state captures.
- [ ] Audit each other context that shares the R1 raster split.
- [ ] Add context-proven dialogue/UI strings one screen at a time.
- [ ] Check Korean glyph readability on every promoted screen.
- [ ] Run cross-screen boot and gameplay smoke tests without untargeted autoplay.
- [ ] Require manual visual evidence only for release or high-risk candidates.

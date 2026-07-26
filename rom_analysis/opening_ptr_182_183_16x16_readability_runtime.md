# Two-Record Opening Runtime Proof

Status: **PASS_FOR_TWO_OPENING_CONTEXTS**

Candidate ROM MD5: `d1bd6e285c818ed60890282d8704f80a`

| record | ROM offset / CPU | bounded capture | runtime reads | native visual review | result |
| --- | --- | --- | --- | --- | --- |
| Pointer 182 | `0x071B6` / `$B1A6` | frame 883 | 33/33 matching | Korean glyphs are legible without clipping or overlap | PASS |
| Pointer 183 | `0x071D7` / `$B1C7` | frame 1095 | 25/25 matching | speaker separator and following Korean text have readable spacing | PASS |

The pointer-183 capture begins from the verified opening route, uses one
deliberate acknowledgement of pointer 182, and stops as soon as its target is
complete. No free-form gameplay, enemy handling, or boss progression is used.

Evidence:

- `rom_analysis/opening_ptr_182_183_16x16_p182_capture/analysis.md`
- `rom_analysis/opening_ptr_182_183_16x16_p183_capture/analysis.md`
- `rom_analysis/opening_ptr_182_183_16x16_readability.json`

This proof does not promote the project to a release candidate. It only proves
the scoped renderer, font, control-token handling, and two opening contexts.

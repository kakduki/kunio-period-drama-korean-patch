# Three-Record Opening Korean Runtime Verification

Status: **PASS_FOR_THREE_OPENING_CONTEXTS**

This is a bounded development proof, not a release candidate. The generated
ROM and IPS stay local and ignored; this report, the catalog, scripts, and PNG
evidence are reproducible repository artifacts.

## Candidate

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM MD5: `46cedd1da6d49643f5dd6bc4895ce706`
- English-reference IPS SHA-256:
  `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`
- Font: scene-local paired 8x16 cells rendered as readable 16x16 Korean.
- Scope guard: pointer-record base range `$B1A6-$B1E0`; only pointer entries
  182-184 may move. Pointer 185 remains `$B1F8`.

The English patch supplies only pointer, source-slot, CHR, and relocation
structure. Japanese base-ROM captures supply the translation context.

| pointer | candidate ROM / CPU | Korean text | bounded capture | target reads | visual |
| --- | --- | --- | --- | --- | --- |
| 182 | `0x071B6` / `$B1A6` | `쿠니오: 서둘러! 분조목 위험!` | frame 883 of 920 | 32/32 | PASS |
| 183 | `0x071D6` / `$B1C6` | `오코토: 쿠니오! 기다렸어!` | frame 1093 of 1180 | 25/25 | PASS |
| 184 | `0x071EF` / `$B1DF` | `쿠니오: 오코토, 오랜만.` | frame 1399 of 1430 | 23/23 | PASS |

Pointer 184's Japanese source context was captured independently from the base
ROM at frame 1401 with 24/24 matching reads. The Korean line is therefore not
translated from the English patch.

## Bounded Evidence

- Pointer 182: `rom_analysis/opening_ptr_182_184_16x16_p182_capture/analysis.md`
- Pointer 183: `rom_analysis/opening_ptr_182_184_16x16_p183_capture/analysis.md`
- Pointer 184: `rom_analysis/opening_ptr_182_184_16x16_p184_capture/analysis.md`
- Base Japanese context for pointer 184:
  `rom_analysis/opening_ptr_184_base_probe_capture/opening_dialogue_frame_001401_screen.png`

Each Lua route has a named byte target, a hard frame cap, an exactly bounded
input sequence, one screenshot condition, and `lua_done` as the successful
stop. It does not depend on combat, boss spawning, or free-form gameplay.

## What This Does Not Prove

- Menu, status, item/shop, and event/boss text use separate renderer/context
  families and remain `UNKNOWN`.
- The 20-glyph allocation is only proven for these three opening records.
- This is not a full script translation, a compatibility test of all gameplay,
  or a release package.

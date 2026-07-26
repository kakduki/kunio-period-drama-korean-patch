# Patched ROM Report

Status: **PASS_FOR_THREE_OPENING_CONTEXTS**

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM MD5: `46cedd1da6d49643f5dd6bc4895ce706`
- English reference IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`
- Pointer 182: `0x05F40` -> `0x071B6` / `$B1A6`, 32 bytes.
- Pointer 183: `0x05F42` moves `$B1CB` -> `0x071D6` / `$B1C6`, 25 bytes.
- Pointer 184: `0x05F44` moves `$B1E0` -> `0x071EF` / `$B1DF`, 23 bytes.
- Pointer 185 remains `$B1F8`; the range guard permits only entries 182-184.
- Changed spans: 129; changed-byte scope audit: PASS; escaped bytes: 0.
- Font profile: `readable` (14 px, BOX resampling, threshold 145), 20 scene-local
  Korean glyphs rendered through paired 8x16 cells.
- Runtime evidence: pointer 182 frame 883 `32/32`; pointer 183 frame 1093
  `25/25`; pointer 184 frame 1399 `23/23`; all bounded runs ended `lua_done`.
- Native visual review: PASS for all three screens.

The English patch validates structure only. Pointer 184's Japanese source was
captured from the base ROM before translation. Generated ROM and IPS artifacts
remain local/ignored. This is not a release-ready full translation.

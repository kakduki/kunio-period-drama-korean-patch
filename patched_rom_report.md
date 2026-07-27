# Patched ROM Report

## Historical Opening Candidate

- Status: **PASS_FOR_THREE_OPENING_CONTEXTS**.
- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `46cedd1da6d49643f5dd6bc4895ce706`.
- English reference IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`.
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

## Main Menu Candidate

- Isolated menu smoke: **SOFT_GATE_PASS**; cross-screen page-isolation status: **SOFT_GATE_PASS_ISOLATED_R1_POOL**.
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `d425814e4f1249e2872c9eb09f7fb93d`.
- Static menu template: `0x1F2C1`.
- Raster R1 clone switch: `0x3E` -> `0x46` at `0xEE4D`.
- CHR page pair: `0x3E` -> `0x46`.
- Source Bank 7 CHR pages are preserved; Korean tiles exist only in the cloned Bank 8 pair.
- Declared changed spans: `137`.
- Bounded Items probe: **PASS** source-chain proof; current candidate **PASS**.
- Page-isolation result: isolated Korean menu code pool is active without overlapping Items action codes

The generated ROM and IPS remain local build products. This report records the
reproducible candidate identity without placing copyrighted ROM content in Git.
The English patch validates structure only. Pointer 184's Japanese source was
captured from the base ROM before translation. This is not a release-ready full
translation.

## Combined Development Candidate

- Candidate MD5: `6474e2d857dbbcbf1ce8f1e5d8201c08`.
- Combines the three opening records with the scoped main-menu clone-page
  candidate.
- Complete English-guided pointer catalog: `248` rows; Korean work status is
  `development_verified_opening` for 182-184 and `structural_unknown` for the
  remaining records.
- Bounded opening regression on this exact candidate: pointer 182 frame 883
  `32/32`, pointer 183 frame 1093 `25/25`, pointer 184 frame 1399 `23/23`.
- All three opening routes ended with `lua_done`; no combat or unbounded
  autoplay was used.
- Runtime status: `SOFT_GATE_PASS_COMBINED_CANDIDATE`; release verdict remains
  `UNKNOWN`.

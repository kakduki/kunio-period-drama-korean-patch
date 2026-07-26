# Korean Patch Work Plan

## Current Result

The project has a three-screen, bounded proof of readable Korean dialogue.

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- English reference IPS SHA-256:
  `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`.
- Current candidate ROM MD5: `46cedd1da6d49643f5dd6bc4895ce706`.
- Pointer 182: ROM `0x071B6`, PRG Bank 1, CPU `$B1A6`, frame 883, `32/32`.
- Pointer 183: moved from `$B1CB` to ROM `0x071D6` / CPU `$B1C6`, frame 1093,
  `25/25`.
- Pointer 184: moved from `$B1E0` to ROM `0x071EF` / CPU `$B1DF`, frame 1399,
  `23/23`.
- Native visual review passed for all three 16x16 Korean screens.

This is a development candidate for one opening dialogue family, not a release
build and not evidence for menus, status text, or later events.

## Operating Rules

1. Do not use unbounded FCEUX autoplay. A run requires a named target, hard
   frame cap, deterministic inputs, one capture condition, and an explicit stop.
2. Do not translate all extracted byte sequences. Each record needs its owning
   renderer, controls, ROM range, and Japanese context first.
3. Use the English patch only for structure: pointer table, source slots, CHR,
   and relocation behavior. Do not copy its wording, code, pixels, or headers.
4. Build candidates with narrow changed-byte allowlists and preserve neighbour
   pointer ownership.
5. Mark every record `PASS`, `FAIL`, or `UNKNOWN`; only `PASS` records enter a
   release candidate.

## Next Work

1. Retain the three opening records as a fast regression test only.
2. Build a title/menu catalog and select one direct-navigation target.
3. Establish separate state/route targets for status labels and item/shop text.
4. Obtain reproducible save/debug/cheat states before touching event or boss
   dialogue; never try to solve combat through free-form automation.
5. Expand the glyph pool only when a reachable context has a concrete need.

## Evidence

- Reboot plan: `KOREAN_PATCH_REBOOT_PLAN.md`
- English structure: `rom_analysis/english_patch_implementation_map.md`
- Three-record runtime proof:
  `rom_analysis/opening_ptr_182_184_16x16_readability_runtime.md`
- Source catalog:
  `text_data/korean_scene_batches/opening_ptr_182_184_16x16_readability.json`

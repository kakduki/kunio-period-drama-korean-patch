# Items Candidate Palette Regression Review

Date: 2026-08-06

## Finding

The first Items action candidate reached the correct inventory-list route, but the Korean action glyphs rendered in the dark palette color. The Japanese base screen and the candidate had identical PPU palette bytes, so this was a glyph bitplane issue rather than a palette-register regression.

The generated Korean font asset is currently one-bit-per-pixel: the second 8x16 plane is empty. The original game text uses both NES bitplanes for its bright foreground. scripts/build_patch.py now promotes an empty second plane to the first plane for one-plane glyphs while preserving true 2bpp glyphs.

## Exact Runtime Route

- ROM: verified base CRC32 014D63C9, MD5 0d406a85285b4de8468f0dab6aad5fe5
- Lua route: lua/kunio_main_menu_context_probe.lua
- Extra input: hold A at frames 1900-1911
- Capture: frame 1960
- Bounded run: 1980 frames

## Evidence

| Candidate | Screen hash | Palette bytes | Action verifier |
| --- | --- | --- | --- |
| Japanese base | 6BA8C2892FEE924D624F92575989C1DEA44FE5B4E2E40EDF4846CB948D0866BB | 0F 0C 0F 30 0F 0C 0F 00 0F 0C 0F 0C 0F 0C 0F 30 0F 0F 30 26 0F 0F 25 26 0F 0C 30 30 0F 0F 2A 26 | guard/reference |
| Minimal action, before fix | 9FE73DAA9A41FECD078BC132453B7E36B081334B3A0076D659D9388DF4AD7B04 | identical | PASS |
| Minimal action, after fix | visual verified | identical | PASS |
| Integrated candidate, after fix | captured at C:	mpkunio_fixed_font_extraA_1960.png | identical | PASS |

The corrected integrated candidate displayed the four action labels with the same bright foreground behavior as the Japanese base. The exact source, queue, PPU, and Items bank checks passed.

## Gate

- Static build: PASS
- Correct menu route: PASS
- FCEUX bounded boot/capture: PASS
- Source -> queue -> PPU action chain: PASS
- Korean action readability: PASS for the four action labels in this route
- Whole-game natural progression: UNKNOWN
- Boss/ending dialogue coverage: UNKNOWN
- Release: NOT_READY
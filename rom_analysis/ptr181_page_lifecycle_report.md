# PTR-181 Page Lifecycle Report

## Purpose

This report records the first real non-opening Korean glyph candidate and the
two page-lifecycle strategies tested against it. The test string is a glyph
coverage probe, not release translation.

## Candidates

| candidate | target evidence | stage evidence | gate |
| --- | --- | --- | --- |
| `output/ptr181_bank8_page_probe/` | Korean glyphs visible at frame 392; field preserved | 7200 frames finish, but later capture is black; 48 unique screens | FAIL |
| `output/ptr181_dynamic_page_probe/` | target screen is corrupted when page switches at renderer entry | not promoted | FAIL |
| `output/ptr181_conditional_mapper_probe/` | Korean glyphs visible at frame 392 with field preserved | page restores at frame 622; 7200-frame route finishes normally | PASS |

The static candidate MD5 is `fdcfcf4504b05185fe616518a8cc89cd`.
The dynamic candidate MD5 is `a0889693feb741c6375eb22bc288d7c7`.
The conditional candidate MD5 is `b5f326deabbbdf791d775e9e9b5ad7c0`.

## Static Result

The static candidate clones the original R1 window into Bank 8, writes the
probe glyphs there, and changes the normal mapper setup from `R1=3E` to
`R1=46`. The dedicated PTR-181 probe records:

- target pointer `$B188` seen;
- 74 source/parser events;
- frame-392 mapper `R0=3C, R1=46`;
- Korean glyph tile codes in nametable rows 25 and 27;
- field background and dialogue box preserved.

The bounded stage route reaches combat, but later screens become black. The
reason is global mapper ownership: normal game screens also rely on the R1
window, so a static replacement cannot be promoted.

## Dynamic Result

The dynamic candidate keeps normal mapper setup untouched and retargets the
existing page-switch helper to `$B188`, using `R0/R1=40/42` at the renderer
hook. At the frame-392 capture the mapper has already returned to `3C/3E`,
while the nametable contains the probe codes. The screenshot is corrupted,
showing that the page is not valid for the entire draw lifecycle.

The existing English-derived page-switch code is therefore a structural clue,
not a drop-in solution. A safe implementation needs a helper that executes
from a fixed PRG location and owns the page for every relevant tile fetch,
then restores the original mapping at a proven boundary.

## Conditional Result

The fixed-bank mapper wrapper now checks a renderer-owned scene flag and
screen state `$51`. It selects the already-proven `R0/R1=3C/46` combination
only for PTR-181 and clears the flag on the normal path. The bounded route
records `3C/46` at frame 392, restoration to `3C/3E` at frame 622, normal
combat, a visible late menu at frame 7073, and finite completion at frame 7200.

## Decision

| gate | result |
| --- | --- |
| PTR-181 pointer ownership | PASS |
| Same renderer confirmed | PASS |
| One-screen Korean glyph proof | PASS |
| Whole-route font/page lifecycle | PASS for PTR-181 |
| Release candidate | NO |

The next engineering task is to generalize the proven flag/page selection into
a scene-page table and compile additional pointer records without sharing one
global Korean font page.

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

The static candidate MD5 is `fdcfcf4504b05185fe616518a8cc89cd`.
The dynamic candidate MD5 is `a0889693feb741c6375eb22bc288d7c7`.

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

## Decision

| gate | result |
| --- | --- |
| PTR-181 pointer ownership | PASS |
| Same renderer confirmed | PASS |
| One-screen Korean glyph proof | PASS |
| Whole-route font/page lifecycle | FAIL |
| Release candidate | NO |

The next engineering task is mapper/page lifecycle, followed by a clean rerun
of this same PTR-181 target before any additional dialogue records are added.

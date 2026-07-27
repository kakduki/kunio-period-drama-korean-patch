# Korean Patch Recovery Plan

## Working Rule

Do not use free-running autoplay as a discovery method. Every emulator run needs
a named screen target, a fixed input route, a hard frame cap, and a captured result.

## Sequence

1. Prove a screen context from the base ROM and use the English patch only for structure.
2. Record ROM offset, PRG/CHR bank, renderer or nametable route, and screen evidence.
3. Build one isolated Korean candidate with 16x16 glyphs where readability needs it.
4. Run a bounded boot/screen smoke test and classify PASS, FAIL, or UNKNOWN.
5. Promote only PASS contexts; keep UNKNOWN context work out of release builds.

## Current Position

- Main menu labels: soft-gate PASS.
- Opening dialogue pointers 182-184: historical PASS for three native contexts.
- Menu cursor lifecycle: UNKNOWN.
- Other screens using the shared R1 split: UNKNOWN.
- Dialogue work: continue only from verified renderer contexts, not broad byte scans.

# PTR-181 Screen Renderer Evidence

## Anchor

The bounded stage route reaches a field/location dialogue screen at frame 392.
The corrected PPU nametable dump contains this visible tile-code sequence:

```text
92 A9 9F 92 BB 81 96 87 82 00 9F B4 93 88 AA A6 83 CA
```

The sequence is present in the base ROM at `0x07198`, which is `PTR-181` in
the Bank 1 pointer catalog. The record is in PRG Bank 1, its pointer-table
entry is at `0x05F3E`, and the mapped CPU address is `$B188`.

The same record continues on the second visible dialogue row with:

```text
81 96 87 B4 93 9A 81 CA
```

This is screen evidence, not a candidate inferred only from a CPU address.
The source record ends with the explicit dialogue controls recorded in
`text_data/script_catalog.tsv`.

## Runtime State

At the frame-392 capture, the mapper and PPU state were:

| R0 | R1 | R2 | R3 | R4 | R5 | R6 | R7 | PPUCTRL |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3C` | `3E` | `30` | `31` | `32` | `33` | `02` | `03` | `8C` |

The capture is `rom_analysis/stage_progression_evidence/base_frame_000392_dialogue.png`.
The raw base and candidate captures are intentionally ignored; the probe
script and the selected image are the reproducible evidence set.

## English Reference Meaning

The English pointer map pairs PTR-181 with:

```text
TSUU<BB><00>BROTHER<CA><00>WAIT<CA><FF>
```

This makes PTR-181 a useful first ownership target. It has a known screen
context, a known pointer owner, and a translation reference, while still
being separate from the previously proven opening PTR-182 renderer proof.

## Candidate Result

The v0.4.2 global font-expanded candidate reaches the same frame-392 screen,
but the base dialogue glyphs disappear or render black in the candidate. The
surrounding field remains stable. This classifies the current font strategy as
`FONT_SCOPE_FAIL_PARTIAL_GLOBAL_REMAP`: the font page is being changed outside
the renderer/context that owns the tested record.

The PTR-181 Bank 8 experiments separate the remaining lifecycle problem:

| candidate | target frame | bounded stage route | result |
| --- | --- | --- | --- |
| static `R1=46` page clone | Korean glyphs visible | late black screen; 48 unique screens | FAIL: global mapper regression |
| renderer-entry page switch | target screen corrupted | not promoted | FAIL: page restore timing is unsafe |

The static candidate is useful as a visual ownership proof, but neither page
strategy is a release candidate.

## Decision

| check | result |
| --- | --- |
| Pointer ownership and ROM offset | PASS |
| PRG bank and CPU mapping | PASS |
| Visible base-screen anchor | PASS |
| Same pointer renderer in base and candidate | PASS |
| Current partial Korean promotion | FAIL |

The dedicated probe records 114 source/parser events in both base and v0.4.2
runs, and 74 events in the PTR-181 page candidates. The first
source read is frame 328 at `$B188`, and parser/emit callbacks are aligned at
`$915A`, `$955F`, and `$9593`. Both runs write the same frame-392 nametable
codes and mapper state. The current candidate still renders the glyphs
missing/black, while the static page probe renders a Korean glyph test but
breaks later route screens. The next patch must solve page ownership and
lifecycle from a fixed executable location; a global partial CHR replacement
is not accepted.

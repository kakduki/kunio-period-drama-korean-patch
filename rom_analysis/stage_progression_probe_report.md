# Stage Progression Probe Report

## Runs

| run | ROM | result | final frame | unique screens |
| --- | --- | --- | ---: | ---: |
| base | `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes` | `lua_done` | 7200 | 49 |
| candidate | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua_done` | 7200 | 49 |

The route is implemented by `lua/kunio_stage_progression_probe.lua`.
It enters the known field route through frame 899, then applies a bounded
combat pattern through frame 7200. It is a diagnostic route, not a claim that
the game was completed.

## Checkpoints

| frame | base/candidate behavior | decision |
| ---: | --- | --- |
| 392 | field/location dialogue screen | route entry PASS; visible pointer record anchor |
| 1335 | active field with player and enemies | combat entry PASS |
| 5233 | 1P/COM selection screen after the encounter was not cleared | combat completion UNKNOWN |
| 7200 | finite `lua_done` with no boss target capture | boss route UNKNOWN |

The prior title-screen complaint is not reproduced by this route. It leaves the
title screen and reaches active gameplay before the combat budget begins.

The corrected PPU nametable dump at frame 392 contains the visible record
`PTR-181` at ROM `0x07198` (Bank 1, CPU `$B188`). Its Japanese tile-code
sequence is present in nametable rows 25 and 27. The English reference maps
the same pointer to `TSUU / BROTHER / WAIT`; the full evidence is in
`rom_analysis/ptr181_screen_renderer_evidence.md`.

The dedicated PTR-181 probe confirms that both base and candidate runs read
the record through the same parser at `$915A`, emit through `$955F/$9593`,
and reach the same PPU nametable rows. The candidate therefore fails at the
font page content, not at route entry or pointer dispatch.

## Candidate Regression

The v0.4.2 candidate uses the existing expanded-font ROM plus ten equal-length
PRG replacements. Static scope remains clean, and base/candidate frame 1335
game pixels match apart from the probe overlay. Frame 392 loses the visible
dialogue text in the candidate, while frame 5233 differs in the game
area because shared CHR font slots were changed while that screen still uses
untouched text.

A PTR-181 Bank 8 static-page candidate also passed boot and combat entry and
rendered a Korean glyph test at the dedicated frame-392 probe, but its own
7200-frame route ended on a black screen after the mapper remained at R1=46.
That candidate is `STATIC_PAGE_LIFECYCLE_FAIL`, not a release build.

Classification: `FONT_SCOPE_FAIL_PARTIAL_GLOBAL_REMAP`.

This is the key reset point for the Korean patch. The English patch can remap
its shared alphabet because its script is complete. A partial Korean candidate
cannot reuse that global-font assumption without corrupting remaining Japanese
screens.

## Evidence

- Base captures: ignored raw folder `rom_analysis/stage_progression_probe_base/`.
- Candidate captures: ignored raw folder
  `rom_analysis/stage_progression_probe_v042_candidate/`.
- Selected visual comparisons are retained under
  `rom_analysis/stage_progression_evidence/`.

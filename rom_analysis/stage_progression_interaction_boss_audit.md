# Stage Progression Interaction and Boss Audit

Status: **PASS_INTERACTION_ROUTE_UNKNOWN_BOSS**

## What Was Reached

The bounded route reaches active combat and then reaches a distinct interaction
screen. The screen is present in both the Japanese base ROM and the Korean
candidate, so it is not a Korean renderer boot artifact.

| frame | candidate screen evidence | pointer record | English reference | classification |
| ---: | --- | ---: | --- | --- |
| 1926 | nametable bytes begin `94 8E 00 98 8F 9A` at row 24 | `PTR-135`, ROM `0x0687A` | `WELCOME` | interaction/shop |
| 1986 | nametable bytes begin `8D 96 C0 00 9A C6 93 84 99` at row 24 | `PTR-136`, ROM `0x06882` | `WHAT WOULD YOU LIKE` | interaction/shop |

The matching English reference rows are `PTR-135` and `PTR-136` in
`rom_analysis/english_script_dump.tsv`. The candidate and base nametables differ
only in the expected localized text and nearby event tiles at these checkpoints
(18 bytes at frame 1926 and 42 bytes at frame 1986).

## Bounded Input Findings

- The original route uses `B` during combat and reaches the interaction screen.
- `KUNIO_COMBAT_NO_B=1` avoids that interaction, but the route stalls on the
  same combat area after frame 1456.
- `KUNIO_COMBAT_SWEEP=1` adds a right/down/left/up movement loop; it produces a
  different bounded transition but still does not prove a boss.
- The RAM trace confirms `$0050-$0057` are object status slots, not a single
  enemy-clear byte. They are repeatedly rewritten with values such as `00`,
  `01`, `80`, and `81` while the combat objects are active.

## Release Interpretation

This is useful progression evidence, but it is not boss proof. Do not label the
interaction screen as a boss scene and do not promote any tested single-byte
write as a boss cheat. The next bounded investigation should identify the
enemy-clear transition or a saved-state/scene warp before demanding full-script
visual coverage.

Evidence directories are generated locally and intentionally remain outside the
tracked release inputs:

- `rom_analysis/stage_progression_base_reference/`
- `rom_analysis/stage_progression_dialogue_trace_filtered/`
- `rom_analysis/stage_progression_no_b_candidate/`
- `rom_analysis/stage_progression_sweep_candidate/`
- `rom_analysis/combat_status_trace_baseline/`

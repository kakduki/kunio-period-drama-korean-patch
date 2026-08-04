# Same-Input Combat Route Comparison

Date: 2026-08-05

## Purpose

This bounded comparison checks whether the current Korean candidate changes the
combat route itself. It uses the same FCEUX Lua probe, input mode, frame cap,
and map-route settings against the English structural reference and the
current Korean candidate.

## Inputs

| ROM | size | MD5 |
| --- | ---: | --- |
| `output/english_reference_runtime/kunio_period_drama_english_reference.nes` | 262160 | `63e1d902807981f524af97748cd99500` |
| `output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes` | 368656 | `d062b19d23050cd4e148e22fbfff57b7` |

Probe: `lua/kunio_stage_progression_probe.lua`

Environment for both runs:

```text
KUNIO_MAX_FRAMES=6000
KUNIO_COMBAT_SWEEP=1
KUNIO_ADVANCE_AFTER_COMBAT=1
KUNIO_MAP_SOURCE_ROUTE=1
KUNIO_MAP_DIRECTION=right
```

## Results

| metric | English reference | Korean candidate |
| --- | ---: | ---: |
| completion | `lua_done` at frame 6000 | `lua_done` at frame 6000 |
| unique screens | 10 | 10 |
| combat entry | frame 915 | frame 915 |
| late combat fingerprint | `553498214:7247` | `220996507:7245` |
| boss spawn/dialogue | not observed | not observed |

The late fingerprints differ because the rendered tile data is localized,
but both runs have the same finite route shape, state checkpoints, and lack of
a boss transition. This is evidence against a Korean-renderer boot failure; it
does not prove that the input route clears the encounter.

## Gate

`PASS_FINITE_SAME_GAMEPLAY_NO_BOSS`: the candidate remains bootable and follows
the same bounded combat route as the English reference. The natural
enemy-clear and boss-event gate remains `UNKNOWN`, with failure class
`route_input_or_stage_state_contract_unresolved`.

Do not promote this result as native dialogue proof or a release approval. The
next probe must either identify the enemy-clear state transition or use a
bounded, verified encounter save-state/context.

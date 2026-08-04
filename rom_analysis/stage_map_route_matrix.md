# Bounded Stage Map Route Matrix

Date: 2026-08-05

This is a development probe for the natural combat-to-map transition. It does
not promote a ROM and it does not write a cheat into the candidate. The route
mode is enabled only with `KUNIO_ADVANCE_AFTER_COMBAT=1` and
`KUNIO_MAP_SOURCE_ROUTE=1`.

## Input

- Candidate: `output/full_korean_expanded_candidate/kunio_period_drama_korean_expanded_candidate.nes`
- Candidate MD5: `64b599ca6c502b635d216aebf5ce61b9`
- Lua: `lua/kunio_stage_progression_probe.lua`
- Budget: 2,600 frames per direction; bounded FCEUX completion `lua_done`.
- Entry: the previously verified menu/opening route; combat begins around frame 915.

## Results

| direction | unique screens | last fingerprint | result | classification |
|---|---:|---|---|---|
| left | 10 | `148347524:6748` | `lua_done` | `UNKNOWN_ROUTE_NOT_REACHED` |
| right | 10 | `148347524:6748` | `lua_done` | `UNKNOWN_ROUTE_NOT_REACHED` |
| up | 10 | `148347524:6748` | `lua_done` | `UNKNOWN_ROUTE_NOT_REACHED` |
| down | 9 | `148347524:6748` | `lua_done` | `UNKNOWN_ROUTE_NOT_REACHED` |

All four runs entered combat and produced finite screen changes. None produced
a confirmed enemy-clear marker, map transition, boss-spawn state, or natural boss
dialogue read. The 7,200-frame right-direction follow-up also ended with
`lua_done` and 11 unique screens without a boss marker.

## Decision

- Build: `PASS` for bounded execution and evidence collection.
- Boss route: `UNKNOWN`, failure class `route_input_or_stage_state_contract_unresolved`.
- Promotion: do not apply this route result to the release gate.
- Next probe: correlate object-slot state and the map cursor transition after a
  confirmed enemy-clear event; do not increase the frame budget without a new
  state contract.
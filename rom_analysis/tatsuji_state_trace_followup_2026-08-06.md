# Tatsuji state trace follow-up (2026-08-06)

## Purpose

Record the result of the longest bounded state-trace attempt after the earlier map-entry and English-reference comparisons. This is a development soft-gate artifact, not release evidence.

## Runs compared

| Run | Frames | Unique fingerprints | Result |
|---|---:|---:|---|
| `tatsuji_state_trace_advance` | 6810 | 72 | Reached repeated field/combat screens; no confirmed enemy-clear or boss transition |
| `tatsuji_state_trace_map_route` | 7200 | 12 | Repeated bounded route; no confirmed enemy-clear or boss transition |
| `tatsuji_state_trace_map_route_ab_short` | 1400 | 10 | Entered combat-like screen; no confirmed enemy-clear or boss transition |
| `tatsuji_state_trace_map_route_ab_v2` | 3000 | 10 | Same route shape as short run; no confirmed enemy-clear or boss transition |

## Observations

- The long `advance` run is not stuck on the opening screen: its capture log records entry-screen changes followed by combat-screen changes and 72 unique screen fingerprints.
- The state-machine trace repeatedly executes at `PC=$D207`. The observed `$04F1` values include `00`, `01`, `02`, `04`, `06`, and `12`, so the probe is seeing real state variation rather than a frozen boot state.
- The route still cycles through the same script/state patterns. No trace row establishes a collision hit, enemy-slot clear, boss spawn, boss dialogue, or stage completion.
- This does not justify patching RAM state bytes or promoting a cheat address. Those remain diagnostic-only until a write is correlated with a real hit/miss and a visible game-state change.

## Classification

`PASS_BOUNDED_ROUTE_REACHES_COMBAT_VARIATION; UNKNOWN_NATURAL_ENEMY_CLEAR_AND_BOSS_TRANSITION`

## Next diagnostic

Instrument the collision/damage execution region and compare two controlled runs: player attack with a confirmed target overlap, and the same attack with no target overlap. Promote a state address only if the differing write is followed by a visible slot removal or boss transition. Until then, the release gate remains `NOT_READY` and the Korean candidate remains limited to the 14 native opening pointer records.
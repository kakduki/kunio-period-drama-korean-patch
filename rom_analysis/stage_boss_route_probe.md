# Stage/Boss Route Probe

Status: **SOFT-GATE UNKNOWN**

This probe is a bounded route experiment for the Korean candidate. It is not a
release gate and does not claim a full playthrough.

## What Changed

- The stage probe now records the script loader at CPU `$D207` and the loaded
  route pointers in zero page `$2C/$2D`, `$28-$2B`, and `$1A/$1B`.
- The optional advance route follows the documented encounter-map sequence:
  `Start -> B -> direction+B -> direction+A+B`.
- The combat sweep uses `A+B` with direction so the test exercises the attack
  action instead of only moving the player.
- Every bounded exit writes an explicit `lua_done` marker.

## Results

| run | limit | result | evidence |
| --- | ---: | --- | --- |
| map route, A-only sweep | 7,200 frames | PASS for bounded execution; UNKNOWN for boss | `rom_analysis/tatsuji_state_trace_map_route/summary.tsv` |
| map route, A+B sweep | 3,000 frames | PASS for bounded execution; UNKNOWN for boss | `rom_analysis/tatsuji_state_trace_map_route_ab_v2/summary.tsv` |

The A-only route reached `state 01` after the encounter-map input, but did not
produce a proven boss dialogue screen. The A+B route also reached `state 01`
and ended with `lua_done`; it did not reach a confirmed post-combat dialogue
or next-stage state within the cap.

## Interpretation

The original opening-screen loop is fixed: these runs terminate and reach
multiple gameplay states. The remaining blocker is not the emulator launcher;
it is the unverified enemy-clear/boss-spawn condition. More long runs without
a verified object or progress flag would only repeat the same combat state.

Next work should use a small, explicit RAM/object-state probe or a verified
save/cheat entry for a named encounter. Until then, natural boss route remains
`UNKNOWN` and release status remains `NOT_READY`.

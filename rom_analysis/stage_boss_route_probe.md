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
| one-hit cheat, mixed movement/A+B | 6,000 frames | PASS for bounded execution; UNKNOWN for boss | `rom_analysis/cheat_kill_one_hit_mixed_route_v1/summary.tsv` |
| one-hit cheat, stationary A/B | 6,000 frames | PASS for bounded execution; UNKNOWN for boss | `rom_analysis/cheat_stationary_route_v1/summary.tsv` |
| one-hit cheat, grid movement/A+B | 6,000 frames | PASS for bounded execution; UNKNOWN for boss | `rom_analysis/cheat_grid_route_v1/summary.tsv` |

The A-only route reached `state 01` after the encounter-map input, but did not
produce a proven boss dialogue screen. The A+B route also reached `state 01`
and ended with `lua_done`; it did not reach a confirmed post-combat dialogue
or next-stage state within the cap.

The one-hit probes used the documented `7A02=00` enemy-clear cheat and
exercised mixed, stationary, and grid movement patterns. They all terminated
with `lua_done`, reached multiple gameplay screens, and executed the `$7A02`
decrement routine, but none produced a confirmed boss dialogue or stage
transition. This narrows the remaining issue to the encounter's object/state
conditions rather than the launcher or an opening-screen loop.

## English Reference Comparison

The English reference ROM was run with the same bounded 3,600-frame route and
`KUNIO_COMBAT_MIXED=1` settings as the Korean candidate.

| metric | English reference | Korean candidate |
| --- | --- | --- |
| completion | `lua_done` at frame 3,600 | `lua_done` at frame 3,600 |
| unique screens | 11 | 11 |
| `$7A02` decrement trace | same observed `$AA87` route | same observed `$AA87` route |
| confirmed boss dialogue/transition | no | no |

The timing of a few entry-screen captures differs because the rendered text
and tile data differ, but the combat-state trace and bounded outcome do not.
This indicates that the English patch is a valid structural reference for the
text system, not a ready-made stage warp or boss-clear solution.## Interpretation

The original opening-screen loop is fixed: these runs terminate and reach
multiple gameplay states. The remaining blocker is not the emulator launcher;
it is the unverified enemy-clear/boss-spawn condition. More long runs without
a verified object or progress flag would only repeat the same combat state.

Next work should use a small, explicit RAM/object-state probe or a verified
save/cheat entry for a named encounter. Until then, natural boss route remains
`UNKNOWN` and release status remains `NOT_READY`.

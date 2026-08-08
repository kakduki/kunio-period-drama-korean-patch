# $7A02 One-Hit Cheat Probe

Date: 2026-08-08

## Purpose

Test whether the externally documented one-hit code can provide a reliable shortcut to the first boss/dialogue route. This is a runtime investigation only; it is not part of the Korean ROM patch and does not modify the source ROM.

## Reference

The Japanese game entry at [GameHacking.org](https://gamehacking.org/game/29423) lists `7A02:00` as “Kill Enemies With 1 Hit”. The code was applied by the bounded FCEUX Lua probe as a RAM write to decimal address `31234` (`0x7A02`) during the combat window.

## Runs

All runs used the verified Japanese base ROM and `lua/kunio_stage_progression_probe.lua`. Input automation was bounded and produced a `lua_done` result; no blind long autoplay was used.

| Mode | Result | Evidence |
| --- | --- | --- |
| Mixed attack route + `$7A02=00` | PASS for bounded execution; boss route UNKNOWN | 13 unique screens, final `$04F1=03`, no later dialogue capture |
| Stationary attack route + `$7A02=00` | PASS for bounded execution; boss route UNKNOWN | 38 unique screens, no boss/dialogue transition |
| Mixed route + bounded post-combat Start/B/A input | PASS for bounded execution; route UNKNOWN | No additional screen transition after the combat state |
| Grid attack route + `$7A02=00` | PASS for bounded execution; boss route UNKNOWN | 11 unique screens, final `$04F1=01`, no boss/dialogue transition |

## Interpretation

The code is useful as a repeatable combat-speed aid, but these runs do not prove that `0x7A02` is the complete enemy-clear condition for this route. The address must remain a runtime probe, not a ROM patch or a claimed boss warp. The remaining uncertainty may include enemy spawn state, stage progression flags, route input timing, or a required event transition that the bounded probe does not reproduce.

## Decision

`CHEAT_EFFECT_OBSERVED_BOSS_ROUTE_UNKNOWN`

Do not add a speculative boss-state write. Keep the next route investigation focused on observed RAM/CPU evidence and the English-reference comparison, while using the realtime overlay for immediate translation review rather than as native ROM functionality.

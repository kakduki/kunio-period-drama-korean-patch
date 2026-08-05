# OAM-directed attack sweep comparison (2026-08-06)

## Runs

Both runs used the clean verified Japanese base ROM, the same 900-frame stage-entry sequence, and optional OAM dumps. The sweep moved through left+down, left, down, right, and up phases. The second run alternated A and B attacks every 128 frames.

| Pattern | Frames | Unique screens | FC65 scans | FAD9 | FC82 | FCEF | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| OAM-directed, A only | 3600 | 10 | 1218 | 0 | 0 | 0 | `UNKNOWN_NO_COLLISION` |
| OAM-directed, A/B mixed | 3600 | 10 | 1211 | 0 | 0 | 0 | `UNKNOWN_NO_COLLISION` |

Both runs completed with `lua_done`. The mixed-button run produced 581 branch-trace rows and 10 OAM captures; the A-only run produced 486 branch-trace rows and 10 OAM captures.

## Conclusion

The new directional inputs do move the visible sprite groups and reach the same bounded combat-like route, but neither attack button pattern reaches the collision dispatch or slot-clear paths. This rules out the narrow hypothesis that the previous failure was only caused by using the wrong attack button or a single fixed direction. It does not prove that no collision route exists elsewhere in the game.

No RAM state or cheat address was written. No boss or enemy-clear state was promoted. The next evidence-bearing route must use a manually verified encounter state/save or trace the actual collision eligibility/object class before more automated movement is attempted.

## Reproducible options

- `KUNIO_COMBAT_OAM_SWEEP=1` enables the OAM-directed directional pattern.
- `KUNIO_COMBAT_OAM_SWEEP_MIXED=1` alternates A/B attack buttons within that pattern.
- `KUNIO_OAM_TRACE=1` writes 256-byte OAM dumps beside captures.

Release remains `NOT_READY`.
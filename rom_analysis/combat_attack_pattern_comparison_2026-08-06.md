# Combat attack-pattern comparison (2026-08-06)

## Scope

Two bounded runs used the verified Japanese base ROM and the same stage-entry input. Only the post-entry attack pattern changed. FCEUX recorded combat branch execution, slot scans, object execution, and RAM writes. No state bytes or cheat values were injected.

## Results

| Pattern | Frames | Unique screens | FC65 slot scans | FAD9 collision dispatch | FC82 slot-clear dispatch | FCEF slot clears | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Stationary mixed attack | 2400 | 9 | 652 | 0 | 0 | 0 | `UNKNOWN_NO_TARGET_OVERLAP` |
| Grid movement attack | 2400 | 10 | 639 | 0 | 0 | 0 | `UNKNOWN_NO_TARGET_OVERLAP` |

The stationary run recorded 181 branch-trace rows and 662 object-trace rows. The grid run recorded 294 branch-trace rows and 646 object-trace rows. Both runs reached the bounded combat-like route and completed with `lua_done`.

## Interpretation

- The runs are not opening-screen-only loops; they reach changing field/combat fingerprints and execute the slot/object loops.
- The absence of `FAD9`, `FC82`, and `FCEF` in both patterns means there is no evidence of a collision hit, enemy removal, or boss-triggering clear in these runs.
- The result does not identify a safe cheat address and does not justify writing RAM state. It also does not prove that the ROM or Korean candidate is broken, because the comparison used the clean Japanese base.
- The next route diagnostic must establish target overlap first, preferably by tracing player and object screen coordinates or by using a manually verified save/state at an encounter. Longer free-running autoplay is not evidence for the missing gate.

## Source outputs

- `C:\tmp\kunio_collision_stationary_2400_2026_08_06`
- `C:\tmp\kunio_collision_grid_2400_2026_08_06`

## Classification

`PASS_COMBAT_LOOP_REACHED; UNKNOWN_COLLISION_AND_NATURAL_BOSS_ROUTE`

Release status remains `NOT_READY`.
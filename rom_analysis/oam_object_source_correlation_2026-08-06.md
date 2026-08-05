# OAM-to-object source correlation (2026-08-06)

## Scope

The OAM writer trace was extended with the renderer source bytes `$0010-$0013`, object-workspace bytes `$0430-$0437`, `$0706`, `$07BC`, `$07E4`, and state/coordinate candidates `$0028-$002D`. This permits comparing the sprite record and object state at the same CPU write event.

## Run

The 1,400-frame OAM-directed base-ROM run completed with `lua_done`, 9 unique screen fingerprints, and 22,380 post-entry OAM writes. The run used `KUNIO_COMBAT_OAM_SWEEP=1`, `KUNIO_OAM_TRACE=1`, `KUNIO_OAM_WRITE_TRACE=1`, and `KUNIO_COMBAT_OBJECT_TRACE=1`.

## Observed signatures

At the `$8438/$843D/$8442/$8447` active-sprite writer family, repeated workspace signatures included:

| `$0430-$0437` | `$0706` | Count | Interpretation |
|---|---:|---:|---|
| `00 00 00 00 00 00 00 00` | `04` | 421 | Renderer activity with no nonzero object workspace bytes in this snapshot |
| `00 00 3B B7 B7 56 00 00` | `00` | 160 | Repeated object/render signature |
| `00 00 3B B7 B7 56 00 00` | `07` | 92 | Same signature with a different object index/state |
| `00 00 58 78 97 07 00 00` | `00` | 23 | Separate active-render signature |

The source fields confirm that `$0010-$0013` are the four values copied into the OAM record, while the workspace fields vary independently across render calls. This is runtime correlation evidence, but it does not yet identify the semantic role of each object or prove collision eligibility.

## Classification

`PASS_RENDERER_SOURCE_CORRELATION; UNKNOWN_PLAYER_ENEMY_ROLE_AND_COLLISION_ELIGIBILITY`

No RAM state or cheat address was promoted. FAD9 collision dispatch, FC82 slot-clear dispatch, and FCEF slot clearing remain zero in the associated sweep. The next diagnostic should correlate these signatures with a controlled visible overlap or with the object-slot status read immediately before an attack frame. Release remains `NOT_READY`.
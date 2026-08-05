# OAM shadow write ownership trace (2026-08-06)

## Instrumentation

`KUNIO_OAM_WRITE_TRACE=1` records writes to CPU `$0200-$02FF` after `KUNIO_OAM_WRITE_TRACE_START` (default `$900`). Each row contains frame, OAM address, byte value, PC, registers, and the current gameplay state bytes. The trace is capped at 120,000 rows and does not alter ROM or RAM.

## Verification

The 1,400-frame OAM-directed run completed with `lua_done`, 9 unique screen fingerprints, and 22,380 post-entry OAM write rows. The run used `KUNIO_COMBAT_OAM_SWEEP=1`, `KUNIO_OAM_TRACE=1`, and `KUNIO_OAM_WRITE_TRACE=1`.

Most frequent post-entry writers were:

| PC | Rows | Observed role |
|---|---:|---|
| `$8438`, `$843D`, `$8442`, `$8447` | 2,139 each | Four-byte OAM record writer; writes active sprite Y/tile/attribute/X fields |
| `$DB32`, `$DB35`, `$DB38`, `$DB3B`, `$DB40`, `$DB43`, `$DB46`, `$DB49` | 1,296 each | Repeated hidden-sprite/OAM clearing or fill path |
| `$DAEB`, `$DAEE`, `$DAF1`, `$DAF4` | 864 each | Additional OAM fill path |

The `$8438` family writes the four bytes of each sprite record at offsets such as `$02FC-$02FF`, with X acting as the record offset. This establishes a concrete runtime owner for rendered sprite data; it is stronger evidence than reading final OAM snapshots alone.

## Classification

`PASS_OAM_WRITE_OWNERSHIP; UNKNOWN_COLLISION_ELIGIBILITY`

The trace does not itself prove a hit or enemy removal. Next, correlate the `$8438` writer's source values with object-slot fields and compare frames immediately before/after an intended attack overlap. Release remains `NOT_READY`.
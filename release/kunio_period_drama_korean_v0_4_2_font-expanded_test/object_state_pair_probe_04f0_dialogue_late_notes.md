# Object State Pair Probe 0x04F0 Dialogue-Late Values

This probe wrote the top `0x04F0` object/state block fields recommended by `object_state_pair_plan.md`:

- `$04FA = $30`
- `$04F1 = $02`
- `$04FB = $31`
- `$04FC = $32`

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Environment: `KUNIO_STATE_WRITES=0x04FA=0x30,0x04F1=0x02,0x04FB=0x31,0x04FC=0x32`
- Target table: `lua/kunio_broad_scan_candidate_targets.lua`
- Active broad-scan target matches: `0`
- Visual result: the run reached the same town/street screen pattern as `$04FA = $30` and `$04FB = $31`, not a Tatsuji, Heishichi, or Kajiya proof screen.

## Decision

The `0x04F0` object-state block is not enough to force a useful scene when written with the dialogue-late values from existing dumps. Further progress likely needs enemy-clear counters, event flags, or a trace around the moment an enemy wave resolves rather than more writes to this block.

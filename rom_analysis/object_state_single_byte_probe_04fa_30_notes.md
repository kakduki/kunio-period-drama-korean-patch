# Object State Single-Byte Probe 0x04FA = 0x30

This probe wrote only `$30` to CPU RAM `$04FA`, the top object/enemy-state candidate from `object_state_probe_candidates.md`.

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Address: `$04FA`
- Value: `$30`
- Target table: `lua/kunio_broad_scan_candidate_targets.lua`
- Active broad-scan target matches: `0`
- Visual result: the run reached the same town/street screen pattern as the failed direct runtime-flag writes, not a Tatsuji, Heishichi, or Kajiya proof screen.

## Decision

`$04FA = $30` alone is not a scene/boss warp. Continue with object-state candidates only if the next probe changes screen context; otherwise shift toward paired-state probes or identifying enemy-clear counters from trace/state transitions.

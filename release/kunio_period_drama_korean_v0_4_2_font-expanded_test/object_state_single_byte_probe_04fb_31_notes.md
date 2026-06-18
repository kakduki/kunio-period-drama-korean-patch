# Object State Single-Byte Probe 0x04FB = 0x31

This probe wrote only `$31` to CPU RAM `$04FB`, the next object/enemy-state candidate after `$04FA`.

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Address: `$04FB`
- Value: `$31`
- Target table: `lua/kunio_broad_scan_candidate_targets.lua`
- Active broad-scan target matches: `0`
- Visual result: the run reached the same town/street screen pattern as `$04FA = $30`, not a Tatsuji, Heishichi, or Kajiya proof screen.

## Decision

`$04FB = $31` alone is not a scene/boss warp. Since `$04FA` and `$04FB` both failed with the same visible result, prioritize identifying paired object-state fields or enemy-clear counters before spending many more runs on adjacent single-byte writes.

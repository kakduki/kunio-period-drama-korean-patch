# State Single-Byte Probe 0x0721 = 0x45

This probe wrote only `$45` to CPU RAM `$0721` during a bounded route script.

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Address: `$0721`
- Value: `$45`
- Target table: `lua/kunio_broad_scan_candidate_targets.lua`
- Active broad-scan target matches: `0`
- Visual result: the run reached the same town/street screen pattern as `$0720 = $B1`, not a Tatsuji, Heishichi, or Kajiya proof screen.

## Decision

`$0721 = $45` alone is not a scene/boss warp. Continue with `$0722 = $C9`, `$0723 = $7A`, or switch to comparing enemy/object state bytes before further runtime-flag writes.

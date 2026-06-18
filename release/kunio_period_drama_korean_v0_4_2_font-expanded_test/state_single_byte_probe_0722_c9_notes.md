# State Single-Byte Probe 0x0722 = 0xC9

This probe wrote only `$C9` to CPU RAM `$0722` during a bounded route script.

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Address: `$0722`
- Value: `$C9`
- Target table: `lua/kunio_broad_scan_candidate_targets.lua`
- Active broad-scan target matches: `0`
- Visual result: the run reached the same town/street screen pattern as `$0720 = $B1` and `$0721 = $45`, not a Tatsuji, Heishichi, or Kajiya proof screen.

## Decision

`$0722 = $C9` alone is not a scene/boss warp. Test `$0723 = $7A`; if that also fails, stop testing this contiguous runtime-flag group as direct warp bytes and switch to object/enemy-state candidates.

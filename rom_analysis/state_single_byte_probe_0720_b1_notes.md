# State Single-Byte Probe 0x0720 = 0xB1

This probe wrote only `$B1` to CPU RAM `$0720` during a bounded route script.

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Address: `$0720`
- Value: `$B1`
- Target table: `lua/kunio_broad_scan_candidate_targets.lua`
- Active broad-scan target matches: `0`
- Visual result: the run reached a town/street screen, not a Tatsuji, Heishichi, or Kajiya proof screen.

## Decision

`$0720 = $B1` alone is not a scene/boss warp. Continue with the next state candidates from `state_cheat_probe_candidates.md`, especially nearby runtime flags `$0721-$0723` and zero-page state bytes only one at a time.

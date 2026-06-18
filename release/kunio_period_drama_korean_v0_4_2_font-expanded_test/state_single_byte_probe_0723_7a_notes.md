# State Single-Byte Probe 0x0723 = 0x7A

This probe wrote only `$7A` to CPU RAM `$0723` during a bounded route script.

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Address: `$0723`
- Value: `$7A`
- Target table: `lua/kunio_broad_scan_candidate_targets.lua`
- Active broad-scan target matches: `0`
- Selected evidence PNG: `rom_analysis/state_single_byte_probe_0723_7a_frame_001325_screen.png`
- Selected target records: `rom_analysis/state_single_byte_probe_0723_7a_frame_001325_target_records.tsv`
- Visual result: the run reached a town/street screen with a visible Japanese dialogue line at the bottom, but not a Tatsuji, Heishichi, or Kajiya proof target.

## Decision

`$0723 = $7A` is not sufficient proof for patch promotion because none of the broad-scan target bytes matched. It is more interesting than `$0720-$0722` because it reached a dialogue-like screen, but the contiguous `$0720-$0723` runtime-flag group should not be treated as direct boss/scene warp bytes from single-byte writes alone.

Next work should compare object/enemy-state candidates or pair this state with route/input changes instead of continuing isolated writes in this runtime-flag group.

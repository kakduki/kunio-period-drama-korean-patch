# Object State Pair 0430 Route Probe

## Candidate

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM MD5: `0a983c3d8494444935f000963f415253`
- Lua script: `lua/kunio_stage_progression_probe.lua`
- Capture directory: `rom_analysis/object_state_pair_0430_route_v1/`
- Frame cap: `7,200`

## Probe

The recommended combat-window state block was written during the bounded
route:

```text
0x0432=0x00, 0x0434=0x00, 0x0435=0x00, 0x0439=0x00
```

## Result

- Status: **UNKNOWN_NO_BOSS_TRANSITION**.
- The route reached combat and produced additional screen fingerprints at
  frames `2172` and `2665`.
- The run completed at frame `7200` without a confirmed enemy-clear marker,
  boss spawn, boss dialogue, or boss screen.
- The state block is not promoted as a scene warp or release cheat.

The observed combat changes are insufficient to identify a boss transition.
The bounded run terminated with `lua_done`, so it did not loop indefinitely at
the opening screen.

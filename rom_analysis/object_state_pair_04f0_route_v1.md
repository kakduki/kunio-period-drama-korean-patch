# Object State Pair 04F0 Route Probe

## Candidate

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM MD5: `0a983c3d8494444935f000963f415253`
- Lua script: `lua/kunio_stage_progression_probe.lua`
- Capture directory: `rom_analysis/object_state_pair_04f0_route_v1/`
- Frame cap: `7,200`

## Probe

The recommended paired values from the object-state plan were written during
the combat window:

```text
0x04FA=0x30, 0x04F1=0x02, 0x04FB=0x31, 0x04FC=0x32
```

## Result

- Status: **UNKNOWN_NO_BOSS_TRANSITION**.
- The route reached combat and produced additional screen fingerprints at
  frames `2172`, `2665`, `6995`, and `7085`.
- The run completed at frame `7200` without a confirmed enemy-clear marker,
  boss spawn, boss dialogue, or boss screen.
- The paired values are not promoted as a scene warp or release cheat.

The pair is more active than the isolated `$04FA`/`$04FB` probes, but the
observed screen changes are not sufficient to identify a boss transition.

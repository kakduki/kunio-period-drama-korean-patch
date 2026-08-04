# Enemy Slot Zero Route Probe

## Candidate

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM MD5: `0a983c3d8494444935f000963f415253`
- Lua script: `lua/kunio_stage_progression_probe.lua`
- Capture directory: `rom_analysis/enemy_slots_zero_route_v1/`
- Frame cap: `7,200`

## Probe

During the combat injection window, RAM `$0050-$0057` was repeatedly written
as zero. Existing RAM traces identify this range as object-status slots, so
this was a bounded test of the enemy-clear/boss-transition hypothesis.

Environment:

```text
KUNIO_EXTRA_DIALOGUE_START=1
KUNIO_COMBAT_MIXED=1
KUNIO_ADVANCE_AFTER_COMBAT=1
KUNIO_STATE_WRITES=0x0050=0,0x0051=0,0x0052=0,0x0053=0,0x0054=0,0x0055=0,0x0056=0,0x0057=0
KUNIO_STATE_WRITE_START=900
KUNIO_STATE_WRITE_END=7000
```

## Result

- Status: **UNKNOWN_NO_BOSS_TRANSITION**.
- The ROM reached the known opening, field, and combat screens.
- The bounded run recorded additional screen fingerprints at frames `3465`
  and `4904`, then ended normally at frame `7200`.
- No boss-spawn, enemy-clear, boss dialogue, or boss-screen marker was
  observed.
- The zero writes are not promoted as a cheat and must not be used as a
  release route.

This result narrows the search: object slots are not proven to be a sufficient
enemy-clear control when continuously forced to zero. The natural boss/event
gate remains open.

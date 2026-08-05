# OAM sprite-position probe (2026-08-06)

## Purpose

Add an optional OAM shadow-RAM dump to the bounded stage probe so the combat route can distinguish visible sprites from actual target overlap. The new `KUNIO_OAM_TRACE=1` option writes one 256-byte `frame_*_oam.bin` beside each screen capture. It does not modify the ROM or game RAM.

## Verification

Run:

```text
python scripts/run_fceux_lua_analysis.py --rom "rom\\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\\kunio_stage_progression_probe.lua --frames 1400 --lua-env KUNIO_COMBAT_GRID=1 --lua-env KUNIO_OAM_TRACE=1
```

Result: `lua_done`, 10 unique screen fingerprints, and 10 OAM dumps of exactly 256 bytes.

## Position evidence

At frame 1139, visible sprite groups include clusters around X=`$58-$61`, X=`$6D-$76`, and X=`$45-$4D`. At frame 1229, the same central groups are around X=`$5C-$65`, while another group remains around X=`$E8-$F0` and a separate group is around X=`$48-$50`. These are screen-space sprite positions from the OAM shadow, not inferred RAM addresses.

The captures demonstrate that the route reaches real sprite-rendered scenes, but the current attack patterns do not establish which group is the player target or produce a confirmed overlap. FAD9 collision dispatch, FC82 slot-clear dispatch, and FCEF slot clearing remain zero in the paired attack comparison.

## Classification

`PASS_OAM_CAPTURE; UNKNOWN_PLAYER_TARGET_IDENTITY_AND_COLLISION_OVERLAP`

## Next use

Use OAM clusters together with player input and object-slot trace. Build a short directional sweep that moves the player toward the nearest non-player cluster, then require both screen-space overlap and a nonzero collision-dispatch trace before promoting any state or cheat hypothesis.
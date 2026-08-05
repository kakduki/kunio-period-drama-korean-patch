# Targeted Overlap Probe

Date: 2026-08-06

## Run

- ROM: verified Japanese base, MD5 0d406a85285b4de8468f0dab6aad5fe5
- Lua: lua/kunio_target_overlap_probe.lua
- Frames: 2400
- Route: known entry sequence through frame 900, then fixed directional attack phases
- Output: C:/tmp/kunio_target_overlap_probe_fixed_2026_08_06

## Results

- FCEUX completion: lua_done
- Screen captures: 47
- Combat screen reached: PASS
- A captured frame at 1131 shows the player and an enemy sprite overlapping in screen space:
  C:/tmp/kunio_overlap_1131.png
- FAD9 collision dispatches: 0
- FC82 slot-clear dispatches: 0
- FCEF slot clears: 0
- Final state sample: 04F1=02, 04FA=42, 04FB=47, 04FC=35

## Classification

PASS_COMBAT_OVERLAP_SCREEN_NO_KNOWN_COLLISION_DISPATCH

This narrows the problem: the route is not stuck at the opening and reaches a visible overlap, but the previously watched addresses are not the collision path for this interaction or the attack has not entered the game's valid hit state. No RAM write or ROM cheat was promoted.

## Next Diagnostic

Trace the execution path from the attack input/object update at the overlap frame and identify the actual damage/collision routine before attempting another state write. Existing FAD9/FC82/FCEF zero counts are retained as negative evidence.
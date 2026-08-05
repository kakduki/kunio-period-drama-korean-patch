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
- A captured frame at 1131 shows two actor sprites overlapping in screen space. Their semantic roles are not yet proven from the trace:
  C:/tmp/kunio_overlap_1131.png
- FAD9 collision dispatches: 0
- FC82 slot-clear dispatches: 0
- FCEF slot clears: 0
- Final state sample: 04F1=02, 04FA=42, 04FB=47, 04FC=35
- Extended execution trace: `overlap_exec_trace.tsv` recorded 2,452 calls to FC6B, 1,839 to FC8F, 615 to 8D02, 613 to FC65, 96 to AA8C, and 96 to AA8E; FAD9/FC82/FCEF remained zero.
- The overlap window therefore reaches the object update and slot-scan paths, but not the known collision/clear dispatches. Slot-relative fields are now recorded for the next run (`0049,X`, `0050,X`, `0057,X`, `0496,X`, `04AC,X`, `04B4,X`).
- Slot evidence in the rerun: slot X=01 retained `0050=81`; slot X=05 retained `0050=80` and `04B4=01`; both remained present while the two sprites crossed. This is useful actor-slot evidence, but it is not sufficient to label slot 5 as an enemy or to promote a cheat.

## Classification

PASS_COMBAT_OVERLAP_SCREEN_NO_KNOWN_COLLISION_DISPATCH

This narrows the problem: the route is not stuck at the opening and reaches a visible overlap, but the previously watched addresses are not the collision path for this interaction or the attack has not entered the game's valid hit state. No RAM write or ROM cheat was promoted.

## Next Diagnostic

Trace the execution path from the attack input/object update at the overlap frame and identify the actual damage/collision routine before attempting another state write. Existing FAD9/FC82/FCEF zero counts are retained as negative evidence.
# Hashi Route Probe

Date: 2026-08-06

## Run

- Base ROM: verified Japanese ROM, MD5 0d406a85285b4de8468f0dab6aad5fe5
- Probe: lua/kunio_stage_progression_probe.lua
- Frames: 7200
- Inputs: combat sweep, dialogue trace, post-combat advance, map-source route, map sweep
- Output: C:/tmp/kunio_hashi_route_probe_2026_08_06

## Evidence

- FCEUX completed with lua_done.
- The run produced 10 screen fingerprints and completed the bounded stage probe.
- Dialogue pointer/source tracing was active and produced source-read and parser logs.
- The target Hashi source bytes A0 92 were not observed in the dialogue source trace.
- The translated byte pair 8B 8C was also not observed as a Hashi target match in this run.
- No confirmed collision dispatch, enemy-slot clear, map transition, boss marker, or boss dialogue appeared.

## Classification

UNKNOWN_ROUTE_NOT_REACHED

This result proves that the bounded route is active and progresses through multiple screens; it does not prove that the ROM is stuck or that the target string is absent. No cheat/state write or Korean candidate promotion was made.

## Next Evidence Needed

A route that reaches the encounter-map or stage/location label must be identified before visual approval of the Hashi candidate. Natural boss progression remains UNKNOWN.
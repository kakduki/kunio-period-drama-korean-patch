# Object Region Execution Trace (2026-08-06)

## Purpose

The earlier object trace showed setup calls at `$AD31/$AD34/$AD60/$AD63` but did
not cover the complete `$AD00-$AD7F` region. This optional trace covers that
region on the English reference ROM without RAM writes, to determine whether
the visible field actors enter a later coordinate/collision routine.

## Run

- ROM: `output/english_reference_runtime/kunio_period_drama_english_reference.nes`
- Lua: `lua/kunio_stage_progression_probe.lua`
- Frames: 2,400
- Input: bounded mixed route
- Options: `KUNIO_COMBAT_OBJECT_TRACE=1`, `KUNIO_COMBAT_OBJECT_REGION_TRACE=1`
- Completion: `lua_done`
- Unique screen fingerprints: 10

## Evidence

- `$AD00`: 1,300 trace rows during the repeated object loop
- `$AD30-$AD7E`: 78 rows at frame 1064 only, the setup/coordinate-table pass
- `$AD31/$AD34/$AD60/$AD63`: setup values observed at frame 1064; no later
  region pass was observed
- `$8D02`: 634 object routine calls
- `$FAD9` collision dispatch, `$FC82` slot-clear dispatch, `$FCEF` slot clears:
  0 in the same route

## Classification

`PASS_OBJECT_REGION_TRACE_NO_COLLISION`

The visible actor loop is active, but this route does not reach a confirmed
enemy-hit/death transition. The trace narrows the next target to the input or
stage-state event that instantiates the later collision objects; it does not
justify a coordinate write, boss warp, or candidate ROM change.

The region option is disabled by default and can be enabled with
`KUNIO_COMBAT_OBJECT_REGION_TRACE=1` together with
`KUNIO_COMBAT_OBJECT_TRACE=1`.
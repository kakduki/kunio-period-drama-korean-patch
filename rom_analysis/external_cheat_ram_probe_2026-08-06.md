# External Cheat RAM Probe (2026-08-06)

## Purpose

A public NES cheat listing identifies `$7A00` and `$7A01` as player health and
`$7A02` as a one-hit enemy code. These values were tested only as per-frame
RAM writes in FCEUX against the English reference ROM. No ROM or candidate was
modified.

## Run

- ROM: `output/english_reference_runtime/kunio_period_drama_english_reference.nes`
- Frames: 3,600
- RAM writes: `$7A00=$44`, `$7A01=$44`, `$7A02=$00`, frames 0-3600
- Input: existing bounded mixed route
- Trace: slot scan and collision dispatch hooks
- Completion: `lua_done`
- Unique screen fingerprints: 11

## Result

- `FC65` slot scans: 1,235
- `FAD9` collision dispatch: 0
- `FAE0`/`FB16` collision selectors: 0
- `FC82` slot-clear dispatch: 0
- `FCEF` slot clears: 0
- Confirmed enemy clear, map transition, or boss dialogue: not observed

The RAM writes changed some screen fingerprints compared with the no-write
reference run, but they did not cause the collision or slot-clear path. The
changed screens are therefore not evidence that the cheat represents a boss
warp or stage-clear flag.

## Classification

`PASS_EXTERNAL_CHEAT_PROBE_NO_ROUTE_ADVANCE`

The cheat remains an unpromoted diagnostic hypothesis. The next useful action
is still to capture a real encounter battle or find the input/state transition
that instantiates active enemy collision objects. Do not bake these writes into
the Korean patch.
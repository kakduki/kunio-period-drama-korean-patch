# Map Entry Input Probe (2026-08-06)

## Purpose

This bounded probe tests the documented encounter-map controller sequence
without writing RAM state or applying a cheat. It is deliberately independent
of the unresolved `$04F1` stage-clear gate so that map accessibility and
natural enemy-clear progression are measured separately.

## Run

- ROM: verified Japanese base `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Lua: `lua/kunio_stage_progression_probe.lua`
- Frames: 1,400
- Input mode: `KUNIO_MAP_ENTRY_PROBE=1`
- Sequence after frame 900: Start, B, right+A, then right+B in bounded phases
- Trace: `KUNIO_COMBAT_SLOT_TRACE=1`
- Output: `C:/tmp/kunio_map_entry_probe_1400_2026_08_06`

## Result

- Completion: `lua_done`
- Unique screen fingerprints: 9
- Combat checkpoints: frames 915, 1049, 1139
- `FC65` slot scans: observed
- `FAD9` collision dispatch: 0
- `FAE0`/`FB16` collision selectors: 0
- `FC82` slot-clear dispatch: 0
- `FCEF` slot clears: 0
- Confirmed map transition or boss dialogue: not observed

## Classification

`PASS_INPUT_PROBE_NO_MAP_OR_COLLISION`

The emulator accepted and processed the input sequence, so this is not a
launcher or first-screen hang. The route still does not reach the collision
path that removes an enemy, and it does not establish a safe boss warp or
clear-state cheat. Natural enemy-clear, map progression, boss dialogue, and
later pointer rows remain `UNKNOWN`; no candidate ROM promotion is authorized.

The next useful collection is a manually controlled or externally recorded
actual encounter battle, followed by a short FCEUX memory/PPU capture at the
moment an enemy disappears. Longer repetition of this route is not evidence.
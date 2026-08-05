# Map Cursor to Field Entry (2026-08-06)

## Objective

Continue from the verified opening route without looping on the mode-selection screen. Use the documented encounter-map input sequence and determine whether cursor travel reaches a real field/encounter state.

## Base and route

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Base SHA-256: `54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a`
- Script: `lua/kunio_stage_progression_probe.lua`
- Inputs: `KUNIO_SELECT_MODE=1`, `KUNIO_ADVANCE_OPENING_DIALOGUE=1`, `KUNIO_OPEN_MAP_AFTER_DIALOGUE=1`, `KUNIO_MAP_ONCE_AFTER_DIALOGUE=1`, `KUNIO_MAP_CURSOR_TRAVEL=1`, `KUNIO_MAP_CURSOR_SWEEP=1`
- No RAM/state writes or cheat codes were used.

The route selects the default mode, advances the opening dialogue, opens the map with Start then B, closes the map menu, and cycles right/down/left/up with A and B pulses.

## Results

| Run | Frames | Result | Evidence |
|---|---:|---|---|
| right cursor travel | 3,000 | PASS map entry | `frame 1890`, map fingerprint `44491645:5845` |
| directional sweep | 5,000 | PASS field transition | `frame 1980`, fingerprint `700361187:6340`, town/field scene visible |
| directional sweep with traces | 8,000 | PASS bounded completion; UNKNOWN encounter | `lua_done`, 17 unique fingerprints, 399 dialogue source-read rows |

The `frame 1890` capture is the encounter map with the player cursor. The `frame 1980` capture is a different rendered scene containing the player and Japanese town/field signage. This confirms the route is no longer trapped at the initial mode-selection screen or map screen.

## Combat gate

The 8,000-frame trace recorded 3,221 frame-counter reads, 3,221 sub-counter reads, six slot-scan starts, 24 low-status reads, and 18 high-status reads. It recorded zero FAD9 collision dispatches, zero FC82 slot-clear dispatches, and zero FCEF slot clears. Therefore this run does not prove an enemy encounter, enemy defeat, boss spawn, or boss dialogue.

## Classification

`PASS_MODE_SELECT_DIALOGUE_MAP_FIELD_ENTRY; UNKNOWN_NATURAL_ENCOUNTER`

This is a useful route milestone and should be retained for later targeted movement/encounter work. It is not a release gate and does not justify promoting a cheat or a ROM patch.

## Reproduction

```powershell
python scripts\run_fceux_lua_analysis.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\kunio_stage_progression_probe.lua --frames 8000 --timeout 240 --final-output C:\tmp\kunio_map_to_field_sweep_2026_08_06 --clean-output --no-dump-hex --no-dump-bin --lua-env KUNIO_SELECT_MODE=1 --lua-env KUNIO_ADVANCE_OPENING_DIALOGUE=1 --lua-env KUNIO_OPEN_MAP_AFTER_DIALOGUE=1 --lua-env KUNIO_MAP_ONCE_AFTER_DIALOGUE=1 --lua-env KUNIO_MAP_CURSOR_TRAVEL=1 --lua-env KUNIO_MAP_CURSOR_SWEEP=1 --lua-env KUNIO_DIALOGUE_TRACE=1 --lua-env KUNIO_COMBAT_SLOT_TRACE=1 --lua-env KUNIO_COMBAT_BRANCH_TRACE=1
```

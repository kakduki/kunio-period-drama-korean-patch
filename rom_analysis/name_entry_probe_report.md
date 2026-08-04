# Name Entry Probe

## Scope

This report records a bounded English-reference run used to reach the documented name-entry screen before attempting the Koganemushi route. The probe does not write ROM, SRAM, or CPU memory.

## Evidence

- English reference: `C:\tmp\kunio_english_reference.nes`
- Probe: `lua/kunio_name_entry_probe.lua`
- Static test: `scripts/test_kunio_name_entry_probe.py`
- Reproducible route: initial setup completion, Start menu `ITEMS -> SETUP`, `A`, then `SELECT`.
- Name-entry screen observed at approximately frame 2175 in the control run.
- Forced captures show the `NAME?` character grid and the initial `KUNIO` name.

## Result

| Check | Result | Note |
|---|---|---|
| Reach name-entry screen | PASS | English reference reached the visible `NAME?` grid without blind autoplay. |
| Bounded input route | PASS | The route ends at the requested frame ceiling. |
| Koganemushi coordinate candidate | UNKNOWN | Input changed the visible name during probing, but the final string was not yet proven as `KOGANEMUSHI`. |
| Natural boss/event route | UNKNOWN | This probe does not claim boss-event access. |

## Next action

Treat the coordinate sequence as a candidate only. Use one-character-at-a-time captures to calibrate cursor origin, repeat behavior, and the `END` cell before using any resulting RAM state as a cheat or patch prerequisite.

## Cursor write trace (bounded v2)

- Run: `C:\tmp\kunio_name_probe\cursor_trace_v2`
- Completion: `PASS` (`summary.tsv` contains `lua_done`, frame 3500, unique=8).
- The write watch captured candidate name-buffer writes at `$04FA-$04FC` around frames 2120-2132, before the Koganemushi input sequence.
- During the candidate sequence, `$0700/$0701` changed repeatedly at the input cadence, but no distinct write transition proved that the `END` cell was accepted or that the secret-event state was entered.
- Result: `UNKNOWN`; no ROM or RAM patch is authorized from this trace.

The previous conclusion remains unchanged: the name-entry route is reproducible, but the Koganemushi coordinate candidate is not yet a verified event trigger. The next bounded probe should isolate one cursor move and one `A` press at a time, then compare the screen/PPU and RAM state before proceeding to map/event routing.

## One-cell calibration (right_a / down_a)

- Runs: `C:\tmp\kunio_name_probe\cal_right_a` and `C:\tmp\kunio_name_probe\cal_down_a`
- Both bounded runs completed with `lua_done` at frame 2250.
- The two directions produced a small, distinguishable screen delta at the stable name-entry frame, confirming that the input path is reaching the name-entry renderer.
- Neither run produced a verified name-buffer update or an `END` acceptance transition in the watched state.
- Result: `UNKNOWN`; direction/cursor mapping is still not sufficient to authorize a secret-code or event-state patch.

The calibration mode is now available through `KUNIO_NAME_CALIBRATION=right_a|down_a|right2_a` for future single-cell tests. It is intentionally separate from the full candidate route.

# Natural combat object trace (2026-08-05)

## Scope

This is a bounded diagnostic run for the verified Japanese base-derived full-pointer Korean candidate. It does not claim a boss clear or a complete gameplay route.

- ROM: `C:\tmp\kunio_full_pointer_rebuild\kunio_period_drama_korean_full_pointer_candidate.nes`
- ROM MD5: `165ede9d7cf426a3f8aa841af4268a44`
- Lua: `lua/kunio_stage_progression_probe.lua`
- Route: fixed menu entry through frame 899, then `KUNIO_COMBAT_MIXED=1`
- Ceiling: 2,200 frames
- Output: `C:\tmp\kunio_natural_object_pc_trace`

## Result

`UNKNOWN_NO_CONFIRMED_HP_FIELD`

The run reached the bounded combat phase and completed with `lua_done`; it did not reach a natural boss/event dialogue. PC-tagged writes in `0x02A8-0x02FF` were concentrated at `DAF1`, `DAF4`, and `8438-8447`.

Observed patterns are consistent with object position, animation, tile, and slot bookkeeping:

- `0x02A8-0x02BC`: repeated `F0` reset values and position-like values.
- `0x02BD-0x02FF`: three-byte groups updated by `843D`, `8442`, and `8447`, consistent with object coordinates/status/render fields.
- No field in this range showed a monotonic damage/death decrement correlated with the mixed attack cadence.
- The separately traced `0x04FA-0x04FD` values were short metadata/dialogue-like updates, not a confirmed enemy HP counter.
- The high-frequency `0x0502`, `0x0503`, and `0x0508` writes are active runtime bookkeeping, but their semantics are not proven.

## Decision

Do not patch any of these addresses as a kill or boss-spawn cheat. A state injection here would be speculative and could corrupt object rendering or route state. Natural boss/event ordering remains `UNKNOWN`.

The probe now supports `KUNIO_RAM_TRACE_OBJECT_PC=1`, which records only `0x02A8-0x02FF` in the existing PC-tagged trace format for a future targeted experiment.
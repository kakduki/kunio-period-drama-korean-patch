# Combat Branch Trace (2026-08-06)

## Purpose

Add an optional execution trace around the existing `$AA87` `DEC $7A02`
observation. The hook is disabled by default and does not write CPU RAM. It
records the neighboring `$AA80-$AA8F` instructions, registers, selected RAM
values, and frame number during the bounded combat route.

## Run

- Base ROM: verified Japanese ROM, MD5 `0d406a85285b4de8468f0dab6aad5fe5`
- Probe: `lua/kunio_stage_progression_probe.lua`
- Options: `KUNIO_EXTRA_DIALOGUE_START=1`, `KUNIO_COMBAT_SWEEP=1`, `KUNIO_COMBAT_BRANCH_TRACE=1`
- Budget: 2,400 frames
- Completion: `lua_done`
- Unique screen fingerprints: `10`
- Trace rows: `181`
- Trace frames: `1060` and `1064`
- Output: `C:/tmp/kunio_combat_branch_trace_2400_2026_08_06/combat_branch_trace.tsv`

## Observations

At both trace frames, the `$AA87` callback occurred 9 times. The observed
values at those callbacks were `$7A00=$3F`, `$7A01=$3F`, `$7A02=$00`, and
`$04F1=$01`. The neighboring `$AA8C/$AA8E` callbacks repeatedly advanced the
X register through a slot-like sequence, while `$AA87` did not produce a
transition in `$7A02` or `$04F1`.

This is consistent with a bounded object/slot processing loop, not proof of a
single enemy-clear byte. It also does not identify a safe write value or a boss
warp. The trace is diagnostic evidence only.

## Gate Decision

- `$7A02` as a boss-clear cheat: `FAIL_NOT_PROVEN`
- `$04F1` as a boss-transition cheat: `FAIL_NOT_PROVEN`
- natural boss transition: `UNKNOWN`
- release status: `NOT_READY`

The optional hook is kept in `lua/kunio_stage_progression_probe.lua` for future
real-hit versus miss comparisons. It is disabled unless
`KUNIO_COMBAT_BRANCH_TRACE=1` is set.
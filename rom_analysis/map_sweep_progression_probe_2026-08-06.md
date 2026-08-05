# Map Sweep Progression Probe (2026-08-06)

Status: `PASS_FINITE_ROUTE_NO_BOSS_TRANSITION`

## Change

`lua/kunio_stage_progression_probe.lua` now accepts `KUNIO_MAP_SWEEP=1`.
After the existing bounded entry/combat route reaches the map branch, it cycles
through `right`, `down`, `left`, and `up` in four 192-frame segments. Each
segment uses the documented `Start`, `B`, direction+`A`, and direction+`B`
phases. The mode remains bounded and never writes game state.

## Run

- ROM: full 244-row Korean development candidate
- Frame cap: `3,600` for the short sweep and `7,200` for the combat-sweep run
- Entry: `KUNIO_EXTRA_DIALOGUE_START=1`
- Combat route: `KUNIO_COMBAT_SWEEP=1`
- Map route: `KUNIO_ADVANCE_AFTER_COMBAT=1`, `KUNIO_MAP_SOURCE_ROUTE=1`, `KUNIO_MAP_SWEEP=1`
- Completion: `lua_done`
- Unique screen checkpoints: `10`

## Result

The run reached active combat and produced the same finite screen sequence as
previous bounded runs. The observed state remained `04F1=01` after combat
setup, so the guarded map branch was not entered and no boss dialogue pointer
was reached. This is a stronger negative result than an unbounded opening-loop
run: the route completed, the map mode was available, and the missing condition
was isolated to enemy-clear/combat completion.

No cheat or state write is promoted. The natural boss route remains `UNKNOWN`.

## Evidence

- Short sweep output: `C:/tmp/kunio_map_sweep_3600_2026_08_06`
- Combat sweep output: `C:/tmp/kunio_map_sweep_combat_sweep_2026_08_06`
- External route reference: https://strategywiki.org/wiki/Downtown_Special%3A_Kunio-kun_no_Jidaigeki_da_yo_Zenin_Shuugou%21/Walkthrough
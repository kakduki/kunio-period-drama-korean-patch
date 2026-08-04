# Focused Combat State PC Trace

## Run

- Candidate: `output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes`
- Probe: `lua/kunio_stage_progression_probe.lua`
- Budget: 7200 frames
- Mode: `KUNIO_COMBAT_MIXED=1`, `KUNIO_RAM_TRACE_PC=1`, `KUNIO_RAM_TRACE_OBJECTS=0`
- Result: `PASS_FINITE_7200`
- Summary: `13` unique screen fingerprints; `lua_done` at frame `7200`

## Findings

- The run enters the bounded combat route and continues through late combat checkpoints. It does not show a boss-spawn transition or boss dialogue within the budget.
- The focused state trace contains `36813` rows after frame `900` across `30` RAM addresses.
- `$0706` is an object-slot iteration index. Its writes occur from fixed-bank object-loop code and are not an enemy-count proof.
- `$04F1` changes from `12` to `01` during the observed combat setup. The callback PCs are `8104` and `F195`; neither is sufficient to prove a boss transition.
- Fixed PRG bank `0C`, CPU `$8101` (`ROM offset 0x18111`) contains `STA $04F1` as part of object/state initialization. This is not promoted as a state warp or cheat.
- `$04FA-$04FD` are repeatedly initialized as object metadata. Their values alone are not treated as enemy HP or a boss trigger.

## Gate

`UNKNOWN_ROUTE_NOT_REACHED`: no safe enemy-clear or boss-spawn contract has been established. No state write or ROM patch is promoted from this run.

The earlier full bounded run remains the smoke evidence for finite execution. This focused run is diagnostic evidence only and is not release proof.

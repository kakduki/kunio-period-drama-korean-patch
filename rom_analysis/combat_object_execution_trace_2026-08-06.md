# Combat Object Execution Trace (2026-08-06)

## Purpose

Trace the fixed-bank routines that statically reference $0430/$0431, which
had appeared in the combat RAM write inventory, without writing any emulated
RAM state.

Command:

    python scripts/run_fceux_lua_analysis.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\kunio_stage_progression_probe.lua --frames 2400 --timeout 75 --final-output C:\tmp\kunio_object_exec_trace_2026_08_06 --clean-output --no-dump-hex --no-dump-bin --no-stagnation-abort --lua-env KUNIO_EXTRA_DIALOGUE_START=1 --lua-env KUNIO_COMBAT_SWEEP=1 --lua-env KUNIO_COMBAT_OBJECT_TRACE=1 --lua-env KUNIO_COMBAT_OBJECT_TRACE_LIMIT=3000

## Evidence

- FCEUX completion: lua_done
- Frames: 2400
- Unique screen fingerprints: 10
- Trace rows: 652 data rows
- $8D02: 642 calls from frames 1065-2401
- $AD31/$AD34/$AD60/$AD63: only at frame 1064
- $CD34: two setup calls at frames 150 and 926
- During every $8D02 call, $0430=$00, $0431=$00, $04F1=$01,
  $0706=$00
- $0432-$0435 varied across the combat route and were read with Y=$05;
  these values behave like object coordinate/render fields.
- No boss dialogue source read, lower dialogue-band PPU write, or boss transition
  was observed.

## Classification

PASS_TRACE_NOT_A_BOSS_FLAG

The traced routines are useful object/coordinate processing evidence, but they
do not identify an enemy-clear counter or a safe boss warp. No RAM cheat or ROM
patch is promoted from this trace. The natural boss route remains
UNKNOWN_NOT_REACHED, and the release gate remains NOT_READY.

The optional trace is controlled by KUNIO_COMBAT_OBJECT_TRACE=1 and is disabled
by default.
# Combat State and Later Dialogue Probe (2026-08-06)

## Purpose

This report records bounded attempts to reach the post-opening pointer records `p196-p197` without treating arbitrary RAM writes as confirmed cheats.

## Persistent enemy-slot write

- Candidate ROM: `C:\tmp\kunio_full_pointer_candidate_244_next\kunio_period_drama_korean_full_pointer_candidate.nes`
- Lua script: `lua/kunio_stage_progression_probe.lua`
- Write: CPU `$0050-$0057 = 00`
- Write window: frames 1400-6500
- Route: mixed combat input, 7200-frame cap
- Result: 11 screen changes and normal bounded completion, but no `p196`/`p197` pointer evidence
- Classification: failed state-cheat hypothesis

The same addresses were previously identified as object status slots, so this result does not establish a single enemy-clear flag.

## `$04F1 = 06` state probe

- Write: CPU `$04F1 = 06`
- Write window: frames 1500-1800
- Route: `ADVANCE_AFTER_COMBAT=1`, map-source route enabled
- Result: state screen changed at frame 1956 and state-machine trace continued, but no `p196`/`p197` pointer evidence appeared
- Classification: state transition unproven; not a boss warp

## Later dialogue batch

The extended target route watched `p196-p201` through frame 8000. It recorded only an incomplete/ambiguous read at `p201` around frame 5020. The associated PPU window began at `$2700`, not the lower dialogue band `$2302`, and no complete target match was recorded. This is classified as a false positive, not dialogue proof.

## Current gate

- `p194-p195`: previously promoted with native source-read and PPU evidence
- `p196-p197`: `UNKNOWN`, not promoted
- `p198-p201`: `UNKNOWN`, not promoted
- Enemy-clear cheat: `UNKNOWN`
- Boss route: `UNKNOWN`
- Release: `NOT_READY`

## Reproduction outputs

- `C:\tmp\kunio_enemy_slots_zero_persistent_2026_08_06\captures.tsv`
- `C:\tmp\kunio_state_04f1_06_map_route_2026_08_06\captures.tsv`
- `C:\tmp\kunio_full_pointer_batch_196_201_renderer\summary.tsv`
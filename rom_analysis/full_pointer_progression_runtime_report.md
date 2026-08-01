# Full Pointer Korean Progression Runtime Report

Status: **PASS_GAMEPLAY_ENTRY_UNKNOWN_BOSS**

## Candidate

- ROM: `output/full_pointer_korean_candidate/kunio_period_drama_korean_full_pointer_candidate.nes`
- MD5: `7844f2d6f6a67e86e23b2f954d5ebf3c`
- Script: `lua/kunio_stage_progression_probe.lua`
- Route option: `KUNIO_EXTRA_DIALOGUE_START=1`
- Frame cap: `7,200`; terminal reason: `lua_done`

## Checkpoints

| frame | phase/evidence | result |
| ---: | --- | --- |
| 392 | first full-pointer dialogue, `$07FF=2A`, `$51=13` | Korean page active |
| 667 | dialogue transition after the extra `Start` input | screen changed |
| 757 | field route, `$07FF=00`, R1 restored to normal `3E` | page lifecycle recovered |
| 915 | combat phase begins | gameplay entry PASS |
| 1,049-2,046 | combat screen changes | 12 additional bounded changes |
| 7,200 | finite run completion | `lua_done` |

The original stage probe did not send the `Start` input needed by this
dialogue route and therefore looked stuck at frame 392. The per-button probe
confirmed that the extra `Start` transition changes the screen and eventually
clears the Korean page state. The updated bounded route reaches active combat
without blind unbounded autoplay.

## Limits

- The route does not prove that every boss is defeated.
- No boss-dialogue pointer was captured by this run.
- This is gameplay-entry and page-lifecycle evidence, not release-wide visual
  approval for all 244 translated records.

## Evidence

- `rom_analysis/stage_progression_probe_full_pointer_candidate_start/summary.tsv`
- `rom_analysis/stage_progression_probe_full_pointer_candidate_start/captures.tsv`
- `rom_analysis/full_pointer_dialogue_input_probe/summary.tsv`

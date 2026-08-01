# Full Pointer Korean Progression Runtime Report

Status: **PASS_GAMEPLAY_ENTRY_PASS_INTERACTION_UNKNOWN_BOSS**

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
| 1,049-1,866 | combat screen changes | combat route remains active |
| 1,926 | distinct event screen | `PTR-135` reverse-maps to English `WELCOME`; interaction/shop |
| 1,986 | distinct event screen | `PTR-136` reverse-maps to English `WHAT WOULD YOU LIKE`; interaction/shop |
| 7,200 | finite run completion | `lua_done` |

The original stage probe did not send the `Start` input needed by this
dialogue route and therefore looked stuck at frame 392. The per-button probe
confirmed that the extra `Start` transition changes the screen and eventually
clears the Korean page state. The updated bounded route reaches active combat
without blind unbounded autoplay.

The same event checkpoints were reproduced on the Japanese base ROM. The
candidate nametable differs only in the localized text and nearby event tiles:
18 bytes at frame 1926 and 42 bytes at frame 1986. This confirms the route is
real gameplay/event behavior, not a Korean patch boot loop.

## Limits

- The route does not prove that every boss is defeated.
- The reached interaction screen is not a boss scene. No boss dialogue or boss
  defeat was captured by this run.
- This is gameplay-entry and page-lifecycle evidence, not release-wide visual
  approval for all 244 translated records.

## Evidence

- `rom_analysis/stage_progression_probe_full_pointer_candidate_start/summary.tsv`
- `rom_analysis/stage_progression_probe_full_pointer_candidate_start/captures.tsv`
- `rom_analysis/full_pointer_dialogue_input_probe/summary.tsv`
- `rom_analysis/stage_progression_interaction_boss_audit.md`

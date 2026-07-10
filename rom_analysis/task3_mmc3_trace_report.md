# Task 3 MMC3 runtime trace — working Mesen path; candidate not reached

**Date:** 2026-07-11

## Requested runtime question

Verify whether the static task-3 lead at file offset `0x052A5` can be reached through the code-shaped `JSR $B295` at physical PRG offset `0x1B24C`, while recording live MMC3 mapping state.

## Corrected runtime method

`/Applications/Mesen2.app/Mesen.app/Contents/MacOS/Mesen` runs this ROM successfully through its Lua test runner when invoked with an actual Lua script:

```sh
Mesen --testRunner --enableStdout task3_mmc3_probe.lua rom/kunio.nes --timeout=45
```

The prior `exit 255` conclusion was invalid: `/dev/null` was supplied where Mesen requires a valid Lua script. No application bundle was modified.

## Evidence produced

| Artifact | Result |
|---|---|
| `task3_mmc3_probe_inputpolled.log` | Mesen exited `0`; 1,800 frames; 36,682 MMC3 `$8000/$8001` register-value writes recorded. |
| `task3_frame600_inputpolled.png` | Mesen exited `0`; visual frame shows the game’s opening dialogue scene (not the title screen). |
| input observation | `INPUT_POLLED_START=true`: Start was injected through Mesen's required `inputPolled` event. |
| `$B295` execution callback | `0` hits during the verified opening-path run. |
| `task3_source_mapper_probe.log` | Single bounded 3,600-frame route with one Start and non-repeating A confirmations; `$B23C` observations `0`, `$C23C` observations `0`, `$B295` hits `0`. End marker: `TASK3_PROBE_END frame=3600 source_observations=0 qualified_source_hits=0 target_hits=0 mapper_values=82625`. |

## Mapper-link evidence boundary

The sole `JSR $B295` instruction is at raw ROM offset `0x1B24C`: 8 KiB PRG bank `13`, offset `0x123C`. Because `$A000–$BFFF` is MMC3-switchable, that CPU operand alone does **not** identify a physical target bank.

Raw `0x052A5` is bank 2 at `$B295` *only when reg7 is 2*. That mapping state was not observed at the `JSR` site. The target bytes (`82 84 7E 91 …`) are also not independently established as a callable routine; CDL marks them unexecuted. Conversely, the JSR site's opcode byte is marked as executed in the existing CDL, but its historical mapper state was not retained.

**Correct status:** the `JSR $B295 → raw 0x052A5` link is an unverified mapper-dependent static lead, not a route condition. No further autoplay should be used to assert it. A valid proof requires one single trace showing the JSR-site CPU execution and live MMC3 reg7 value together.

## Classification

- `runtime_status`: **available**
- `mapper_state_observed`: **yes**
- `input_delivery_verified`: **yes**
- `opening_scene_reached`: **yes**
- `task3_route_status`: **opening path tested; `$B295` not reached**
- `target_scene_reached`: **no**
- `visual_proof_of_target`: **no**
- `release_ready`: **no**

## Evidence boundary

The `JSR $B295` finding remains a static candidate until an in-game branch that executes `$B295` is identified. The verified trace rules out only the automated opening path used here; it does not prove the routine is dead or that `0x052A5` is unreachable in another scene.

No Korean ROM or IPS was generated or changed by this runtime trace.

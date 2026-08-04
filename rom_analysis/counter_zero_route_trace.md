# Counter-Zero Route Trace

Status: **UNKNOWN_COUNTER_ZERO_NO_DIALOGUE**

This is a bounded diagnostic result, not a release proof. It compares the
current full Korean candidate with the English structural-reference runtime
using the same automated combat route.

## Reproduction

- Korean candidate: `output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes`
- Korean candidate MD5: `d062b19d23050cd4e148e22fbfff57b7`
- English reference: `output/english_reference_runtime/kunio_period_drama_english_reference.nes`
- English reference MD5: `63e1d902807981f524af97748cd99500`
- Lua probe: `lua/kunio_stage_progression_probe.lua`
- Route: `KUNIO_COMBAT_MIXED=1`, `KUNIO_ADVANCE_AFTER_COMBAT=0`
- Limit: `KUNIO_MAX_FRAMES=7200`
- Trace: `KUNIO_SRAM_ROUTE_TRACE=1`, `KUNIO_COUNTER_READ_TRACE=1`, `KUNIO_RAM_TRACE_OBJECTS=0`

Both runs ended with `lua_done` at frame 7200. The exact raw outputs were
written outside the repository during the investigation:

- `C:\tmp\korean_sram_exec_route_7200`
- `C:\tmp\english_sram_exec_route_7200`
- `C:\tmp\korean_counter_reads_7200\counter_reads.tsv`
- `C:\tmp\english_counter_reads_7200\counter_reads.tsv`

## Observed Contract

The execution hook is at CPU `$AA87`, a routine label retained from earlier
reports as `dec_7a02_axxx`. In both ROMs the observed values are:

| checkpoint | `$7A01` | `$7A02` | `$04F1` | `$0050-$0053` |
| ---: | ---: | ---: | ---: | --- |
| frame 1060 | `3F` | `00` | `01` | `00 00 00 00` |
| frame 5952 | `03` | `00` | `01` | `9A 0F 00 00` |
| frame 6193 | `00` | `00` | `01` | `9A 0F 00 00` |
| frame 7019 | `00` | `00` | `03` | `00 00 00 00` |

The current trace therefore demonstrates a decrementing `$7A01` value while
`$7A02` remains zero. The old description of this as a confirmed `$7A02`
enemy-clear counter is not supported by this run; the `7A02` name is only a
routine/address label until ownership is proven.

The direct-read trace is narrower: both ROMs executed `LDA $7A01` at CPU
`$AD76` exactly twice at frame `1064`, with `$7A01=$3F`; the other registered
direct references (`$A661`, `$AD86`, `$AD89`) did not execute in the 7,200-frame
route. No direct counter read occurred near frame 6193 or 7019. This makes the
observed `$7A01` decrement a route/setup value, not evidence of an enemy HP or
boss-clear variable.

## Result

Both ROMs produced the same post-counter screen-change frames:

- frame 6995: fingerprint `66564427:0`
- frame 7085: state `$04F1=03`, then final fingerprint at frame 7200

The final fingerprints differ because the Korean candidate has localized tile
data, but the route timing and state checkpoints match. No confirmed dialogue
source read, dialogue parser execution, or dialogue PPU write occurred after
the counter-zero transition in the focused follow-up trace. This is not proof
of a boss screen or boss dialogue.

## Gate Classification

- bounded execution: `PASS`
- same-input Korean/English route shape: `PASS`
- counter-zero event observed: `PASS`
- direct counter-read trace: `PASS` (same two reads in both ROMs)
- enemy-clear ownership: `UNKNOWN`
- boss spawn/dialogue: `UNKNOWN`
- release readiness: `NOT_READY`

The next useful probe is a named encounter checkpoint or a proven object/state
contract. Extending the same free-running route would not add reliable proof.
# Map CRSR Source-Read Probe Result

Date: 2026-08-05

## Probe Contract

- Script: `lua/kunio_map_crsr_source_probe.lua`
- Source CPU window: `$9C59-$9C61`
- Expected English reference bytes: `8D 81 90 38 83 92 93 92 FF`
- Frame cap: `3600`
- Input mode: bounded entry plus `MAP_SOURCE_ROUTE=1`, direction `right`
- State writes: none

## Comparison

| ROM | completion | registered bytes | source reads | unique screens | classification |
| --- | --- | ---: | ---: | ---: | --- |
| English reference | `lua_done` | 9 | 0 | 5 | `UNKNOWN_ROUTE_NOT_REACHED` |
| Japanese base | `lua_done` | 9 | 0 | 5 | `UNKNOWN_ROUTE_NOT_REACHED` |

Both ROMs produced the same bounded screen-count and zero source-read result.
This does not prove that the Map CRSR item is absent, nor does it authorize a
state write. It proves only that this automated route did not reach the source
record in either ROM within the bounded contract.

## Decision

- Source address contract: structurally confirmed as `$9C59-$9C61` for `EN-PRE-167`.
- Runtime ownership: `UNKNOWN`.
- Safe cheat/state write: not authorized.
- Native patch change: none.
- Next evidence: a manual or state-guided shop/map capture that visibly reaches
  the Map CRSR path, followed by source-read and RAM-delta comparison.

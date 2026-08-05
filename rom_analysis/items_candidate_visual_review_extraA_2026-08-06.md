# Items Candidate Visual Review: Exact Route (2026-08-06)

## Run

- ROM: integrated development candidate `full_korean_clean_merged_candidate`
- Lua: `lua/kunio_main_menu_context_probe.lua`
- Capture frame: `1960`
- Required extra input: `A` held during frames `1900-1911`
- Runtime output: `C:\tmp\kunio_integrated_items_extraA_1960_2026_08_06`
- Screenshot: `rom_analysis/items_candidate_visual_review_extraA_2026-08-06.png`

## Evidence

The exact route used by the Japanese guard capture was reproduced. The
candidate completed with `lua_done`, `screen=true`, `ppu_read=true`, and
`ppu_writes=4748`. The candidate nametable fingerprint changed from the guard
screen because the candidate writes the translated tile stream.

The extra source trace reached the item action source through CPU `$B707` and
copied it through `$B70D` into the queue buffer. The capture also contains the
corresponding queue and PPU writes for the item action area.

Screenshot hashes:

- Candidate: `33AEB92E1C5596CEE616A292BBF9B82E2F9A39E765962E79369F7BE77AECB193`
- Japanese guard: `6BA8C2892FEE924D624F92575989C1DEA44FE5B4E2E40EDF4846CB948D0866BB`
- Development route reference: `6BA8C2892FEE924D624F92575989C1DEA44FE5B4E2E40EDF4846CB948D0866BB`

## Gate Decision

| Gate | Result | Reason |
| --- | --- | --- |
| Exact inventory route | PASS | The missing `A` hold at frames 1900-1911 was restored. |
| Candidate inventory screen context | PASS | The reviewed candidate image is the inventory-list layout, not the shop scene. |
| Candidate source/queue/PPU chain | PASS | `$B707` -> `$B70D` -> queue writes -> PPU writes were captured. |
| Korean item/action readability | UNKNOWN | Pixels changed and the intended screen is present, but final visual readability still needs an explicit native review decision. |
| Release promotion | NOT_READY | This remains a development candidate until Korean glyph readability and shared-font regressions pass. |

This supersedes the earlier wrong-context result only for the corrected route;
the earlier report remains as evidence of why the missing extra input mattered.
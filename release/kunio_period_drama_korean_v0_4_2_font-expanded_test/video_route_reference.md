# Video Route Reference

This file records external gameplay-route references that can replace blind FCEUX autoplay.

## Primary Reference

- URL: `https://www.youtube.com/watch?v=W9OHjavh6Lw&t=913s`
- Start time: `00:15:13`
- Purpose: use the same gameplay route as the video to reach menu/dialogue/item screens for Korean patch visual proof.
- Current target: `0x07227` / `Katana`
- Current screen hint: look for a katana/weapon item label.

## Why This Helps

Blind autoplay has repeatedly stayed on or near the opening/title route and has not produced useful manual dump records. A known gameplay video gives a concrete route to mirror:

1. Identify the game state at the reference timestamp.
2. Translate visible movement/menu choices into controller inputs.
3. Encode those inputs in a Lua route script.
4. Run the route against the patched ROM with target-record dumps enabled.
5. Use screenshots and target records as evidence before confirming visual review.

## Current Limitation

The repository does not yet contain extracted controller inputs from the video. The next useful work is to convert the visible route around `00:15:13` into timed FCEUX inputs, then add it as a route-specific Lua script instead of extending blind autoplay.

## Automated Explorer Follow-Up

- Lua: `lua/kunio_input_explorer_v042.lua`
- Latest output: `rom_analysis/fceux_input_explorer_v042/summary.md`
- Result: the first bounded automated route now produces manual-style dumps without user navigation.
- Evidence note: `manual_frame_000362`, `manual_frame_000643`, and `manual_frame_000883` include active target-record matches for `ROM+0x07227` patched bytes (`88 89 8A`). This is stronger than the prior title-screen wait, but visual-context confirmation is still required before marking the row release-ready.

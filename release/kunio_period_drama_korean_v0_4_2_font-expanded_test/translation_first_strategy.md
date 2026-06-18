# Translation-First Patch Strategy

The efficient path is to treat extracted translation/reference data as the patch source, and use FCEUX only to prove that a candidate ROM offset is the visible in-game text instance.

## Current Evidence

- `rom_analysis/translation_pattern_scan.md` scans 144 reference entries and finds 132 ROM hits.
- `rom_analysis/broad_scan_patchability.md` narrows those hits to 7 promotion candidates after screen proof.
- `rom_analysis/v042_text_promotion_readiness.md` shows all 7 promotion candidates are font-ready under the v0.4.2 glyph set.
- `rom_analysis/route_proof_status.md` shows the remaining blocker is not translation or glyph coverage; it is missing CPU-read plus visible screen-context proof.

## Practical Rule

Do not spend long runs on blind autoplay. The game requires normal combat progression before boss/name contexts appear, so automation can waste time replaying the game.

Use this split instead:

1. Patch from the translation/reference queue where length, glyphs, and bank constraints are already satisfied.
2. For unproven boss/dialogue rows, find a route cheat, savestate, or state flag that reaches the relevant scene quickly.
3. Capture the screen with the route-specific watcher.
4. Promote only rows where CPU-read bytes and visible context agree.

## Current Promotion Targets

| route | offsets | purpose |
| --- | --- | --- |
| Kajiya | `0x0440C` | blacksmith/shop or stage label |
| Tatsuji | `0x048F4`, `0x052A5`, `0x05BE5` | boss/name context |
| Heishichi | `0x06294`, `0x0631B`, `0x06359` | boss/name or dialogue context |

## Next Best Work

The next useful emulator work is not another long autoplay pass. It is to identify player map/room coordinates, enemy-clear flags, and boss-spawn state bytes so a Lua script can jump directly to Tatsuji or Heishichi proof screens.

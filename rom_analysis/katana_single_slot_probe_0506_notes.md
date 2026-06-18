# Katana Single-Slot Probe 0x0506

This probe wrote only `0x84` to CPU RAM `$0506` while following the item-list route.

## Result

- Probe Lua: `lua/kunio_katana_single_slot_probe_v042.lua`
- Slot: `$0506`
- Value: `$84`
- `ROM+0x07227` active match: `false`
- Visual result: the route remained on the town/street screen and did not show a Katana-labelled item list.

## Decision

`$0506` alone is not enough to make the Katana label appear. Further single-slot item probing is now lower value than finding game-state/route cheats for boss and dialogue contexts.

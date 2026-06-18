# Katana Single-Slot Probe 0x0503

This probe wrote only `0x84` to CPU RAM `$0503` while following the item-list route.

## Result

- Probe Lua: `lua/kunio_katana_single_slot_probe_v042.lua`
- Slot: `$0503`
- Value: `$84`
- `ROM+0x07227` active match: `false`
- Visual result: the route stayed on the town/street screen and did not show a Katana-labelled item list.

## Decision

`$0503` alone is not enough to make the Katana label appear. Continue with the next single-slot candidates from `katana_inventory_slot_candidates.md`: `$0506`, `$0508`, then `$0509`.

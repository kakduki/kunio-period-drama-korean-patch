# Katana Inventory Probe Notes

The first temporary-state probe wrote the likely Katana low item id `0x84` into narrow CPU/SRAM candidate slots before opening the item list.

## Result

- Probe Lua: `lua/kunio_katana_inventory_probe_v042.lua`
- Run output directory used during analysis: `rom_analysis/katana_inventory_probe_v042`
- Observed effect: the screen changed, but the menu route became unstable and the item list did not show the Katana label.
- `ROM+0x07227` active match remained `false` in the generated target records.
- Visual result: broad candidate writes can corrupt menu rendering, so this should not be treated as visual proof.

## Decision

Do not use broad RAM/SRAM writes as a confirmation method. The next probe should isolate a smaller inventory slot candidate, preferably by tracing the item-list routine or comparing a save/state that actually owns an item.

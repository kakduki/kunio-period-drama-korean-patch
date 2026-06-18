# Katana Single-Slot Probe 0x0508

This probe wrote only `0x84` to CPU RAM `$0508` while following the item-list route.

## Result

- Probe Lua: `lua/kunio_katana_single_slot_probe_v042.lua`
- Slot: `$0508`
- Value: `$84`
- Output folder: `rom_analysis/katana_single_slot_probe_v042_0508`
- `ROM+0x07227` active match: `true` during early route frames, including frame 302.
- Visual result: frame 302 is a black/non-reviewable screen; later visible town/shop frames such as 2276 and 2366 do not show a Katana-labelled item list.

## Evidence Split

- CPU-read evidence exists for `$0508`, but it happens before a usable item-list visual context.
- The later visible route frames have `ROM+0x07227` inactive and therefore cannot approve the Katana visual gate.
- This is not a title-screen loop; the route reaches the town/shop scene, but not the needed item-list label state.

## Decision

`$0508` alone is not enough to make the Katana label appear on a visible item-list screen. Continue with the last remaining candidate_small_probe address, `$0509`, before switching to grouped runtime-state probes.

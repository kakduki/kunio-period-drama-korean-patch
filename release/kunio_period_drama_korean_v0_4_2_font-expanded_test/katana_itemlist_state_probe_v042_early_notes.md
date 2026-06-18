# Katana Item-List State Probe v0.4.2 Early Injection

This probe tested whether the known Katana visual target at `ROM+0x07227`
would become active by forcing the current best inventory/runtime-state bytes
while replaying the proven item-list route from the Katana visual explorer.

## Inputs

- ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Lua: `lua/kunio_katana_itemlist_state_probe_v042.lua`
- Target table: `lua/kunio_v041_conflict_safe_targets.lua`
- Output: `rom_analysis/katana_itemlist_state_probe_v042_early/`
- Frame budget: `3000`
- Injection window: `1500-2520`

## Forced Bytes

```text
0x0502=0x3C
0x0503=0x3E
0x0506=0x01
0x0508=0x9C
0x0509=0x42
0x0700=0x82
0x0701=0x0C
0x0702=0x0C
0x0706=0x00
0x0707=0x6E
0x071F=0x01
```

## Result

Decision: `VISUAL_FAIL_ITEMLIST_EMPTY`

The route progressed beyond the opening/title loop and reached the same
scripted route phases used by the Katana visual explorer. The useful evidence
frames are:

- `manual_frame_001726_screen.png`: captured during the injection window.
- `manual_frame_001816_screen.png`: captured during the injection window.
- `manual_frame_002646_screen.png`: later route frame after the injection window.

At frame `1726`, the `ROM+0x07227` target record was still inactive:

```text
rom_hit=ROM+0x07227
cpu_range=$B216-$B21A
expected_bytes=88 89 8A
active_expected_match=false
record_snapshot=00 00 00 00 90
```

Frame `1816` also stayed inactive for the same target. The forced byte set did
not make the Katana item-list label appear.

## Interpretation

This was not a useful visual proof for the release gate. It also was not simply
a title-screen-only run. The emulator route advanced, but the current forced
inventory/runtime bytes are insufficient to expose the Katana item-list string.

## Next Step

Do not repeat this same write set. The next probe should discover the real
inventory ownership/item-id slots or the menu/shop selection state that causes
the item-list renderer to read `ROM+0x07227`.

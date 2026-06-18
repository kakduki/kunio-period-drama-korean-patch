# Katana Visual Explorer v0.4.2

Focused route evidence for the primary visual target `0x07227` / `Katana`.

## Summary

- Frames recorded: **24**
- Final frame: **3000**
- Item-list frame: **2385**
- Katana ROM hit: `ROM+0x07227`
- Katana active match on item-list screen: `false`
- Item-list snapshot at Katana CPU range: `00 00 00 00 90`
- Decision: The route now reaches the item-list context automatically, but the list is empty. Do not mark Katana visually confirmed until the item is acquired or injected and the label is visible.
- Next step: Find or set the inventory state that makes the Katana item label appear on the reached item-list screen.

## Key Frames

| frame | route | role | image |
| ---: | --- | --- | --- |
| 1905 | `start_right_a` | main menu with item/status choices visible | `rom_analysis/katana_visual_explorer_v042/manual_frame_001906_screen.png` |
| 2385 | `menu_left_a` | item list reached; current inventory says empty | `rom_analysis/katana_visual_explorer_v042/manual_frame_002385_screen.png` |

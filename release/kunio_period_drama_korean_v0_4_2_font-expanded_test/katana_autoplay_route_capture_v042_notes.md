# Katana Autoplay-Route Capture v0.4.2

This probe replays the older `kunio_autoplay_watch.lua` menu route because
earlier PPU logs showed the base-ROM Katana bytes being written around frames
`1976-1984`.

## Inputs

- ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Lua: `lua/kunio_katana_autoplay_route_capture_v042.lua`
- Target table: `lua/kunio_v041_conflict_safe_targets.lua`
- Output: `rom_analysis/katana_autoplay_route_capture_v042/`
- Frame budget: `2100`

## Result

Decision: `VISUAL_FAIL_WRONG_CONTEXT`

The route reached a non-title screen, but the captured frames are the player or
character selection context, not the weapon/item-list context:

- `manual_frame_001943_screen.png`
- `manual_frame_001985_screen.png`
- `manual_frame_002025_screen.png`

The target record for `ROM+0x07227` stayed inactive in the patched ROM captures:

```text
frame=1985
rom_hit=ROM+0x07227
cpu_range=$B216-$B21A
expected_bytes=88 89 8A
active_expected_match=false
record_snapshot=80 99 16 03 B5
```

## Interpretation

The older runtime/PPU evidence is not enough to approve the Katana visual gate.
It appears to be a wrong-context read/write path rather than item-list visual
proof. Keep `0x07227` and the related Katana candidates quarantined until a real
weapon/item-list screen visibly reads the patched label.

## Next Step

Do not repeat this autoplay route for Katana visual proof. Continue with either:

- a true inventory-acquisition/ownership-state discovery path, or
- a manually or script-guided route that reaches a weapon/item list containing
  the Katana item rather than the empty `なにもない` list.

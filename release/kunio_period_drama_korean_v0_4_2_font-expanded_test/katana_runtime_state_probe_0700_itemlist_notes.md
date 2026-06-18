# Katana Runtime-State Probe 0700 Item-List Values

This probe wrote the item-list observed runtime-state values into CPU RAM while following the Katana route.

## Writes

- `$0700 = $82`
- `$0701 = $0C`
- `$0702 = $0C`
- `$0706 = $00`
- `$0707 = $6E`
- `$071F = $01`

These values came from comparing `rom_analysis/katana_visual_explorer_v042/manual_frame_001906_cpu_ram.bin` with `manual_frame_002385_cpu_ram.bin`.

## Result

- Probe Lua: `lua/kunio_state_single_byte_probe.lua`
- Target table: `lua/kunio_v041_conflict_safe_targets.lua`
- Output folder: `rom_analysis/katana_runtime_state_probe_0700_itemlist_targets`
- `ROM+0x07227` active match: `true` during early route frames, including frame 362.
- Visual result: frame 362 is an in-game field/dialogue screen, not the Katana item-list screen.
- Later visible frames such as 1445 and 2033 reach route/shop scenes, but `ROM+0x07227` is inactive and no Katana item-list label is visible.

## Decision

The run was not stuck on the title/opening screen, but the grouped `$0700-$071F` item-list values did not force a usable Katana item-list visual context. Treat this as `VISUAL_FAIL_ROUTE_PROGRESS`.

Next probes should avoid repeating only these runtime flags. Move toward either paired menu/inventory state that includes `$0500-$050F` plus `$0700-$071F`, or toward a route/menu script that selects the item-list screen after the shop route is already visible.

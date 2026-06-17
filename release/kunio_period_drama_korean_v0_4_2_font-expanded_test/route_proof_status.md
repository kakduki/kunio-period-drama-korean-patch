# Route Proof Status

This report turns the three route-specific FCEUX watchers into a short proof checklist.

## Summary

- Routes: **3**
- Targets: **7**
- CPU-read matched targets: **0**
- Visual-confirmed targets: **0**
- Broad dump status: `no_manual_broad_scan_dump_records`
- Rule: CPU-read bytes plus visible screen context are both required before promotion.

| route | group | status | targets | matched | visual | next step |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | Kajiya | `no_dump_records` | 1 | 0 | 0 | Do not keep blind autoplay running; manually reach this route's screen and press D in its route watcher. |
| 2 | Tatsuji | `no_dump_records` | 3 | 0 | 0 | Do not keep blind autoplay running; manually reach this route's screen and press D in its route watcher. |
| 3 | Heishichi | `no_dump_records` | 3 | 0 | 0 | Do not keep blind autoplay running; manually reach this route's screen and press D in its route watcher. |

## Route Watchers

### Route 1: Kajiya

- Watch Lua: `lua/kunio_manual_route_kajiya_capture_watch.lua`
- Target Lua: `lua/kunio_route_kajiya_targets.lua`
- Screen hint: look for a blacksmith/shop or blacksmith-stage label

| label | ROM | CPU range | matches | visual verdict |
| --- | --- | --- | ---: | --- |
| `broad_0440c_kajiya` | `0x0440C` | `0x840C-0x840E` | 0 | `` |

### Route 2: Tatsuji

- Watch Lua: `lua/kunio_manual_route_tatsuji_capture_watch.lua`
- Target Lua: `lua/kunio_route_tatsuji_targets.lua`
- Screen hint: look for a visible Tatsuji boss/name context

| label | ROM | CPU range | matches | visual verdict |
| --- | --- | --- | ---: | --- |
| `broad_048f4_tatsuji` | `0x048F4` | `0x88F4-0x88F6` | 0 | `` |
| `broad_052a5_tatsuji` | `0x052A5` | `0x92A5-0x92A7` | 0 | `` |
| `broad_05be5_tatsuji` | `0x05BE5` | `0x9BE5-0x9BE7` | 0 | `` |

### Route 3: Heishichi

- Watch Lua: `lua/kunio_manual_route_heishichi_capture_watch.lua`
- Target Lua: `lua/kunio_route_heishichi_targets.lua`
- Screen hint: look for a visible Heishichi name/dialogue context

| label | ROM | CPU range | matches | visual verdict |
| --- | --- | --- | ---: | --- |
| `broad_06294_heishichi` | `0x06294` | `0xA294-0xA297` | 0 | `` |
| `broad_0631b_heishichi` | `0x0631B` | `0xA31B-0xA31E` | 0 | `` |
| `broad_06359_heishichi` | `0x06359` | `0xA359-0xA35C` | 0 | `` |


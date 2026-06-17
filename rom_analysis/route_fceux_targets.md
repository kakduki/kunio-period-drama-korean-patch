# Route FCEUX Targets

These route-specific target tables and watcher wrappers narrow the manual broad-scan proof pass to one screen context at a time.

- Routes: **3**
- Targets: **7**

## Route Watchers

| route | group | targets | target lua | watcher lua | ROM offsets |
| ---: | --- | ---: | --- | --- | --- |
| 1 | Kajiya | 1 | `lua/kunio_route_kajiya_targets.lua` | `lua/kunio_manual_route_kajiya_capture_watch.lua` | `0x0440C` |
| 2 | Tatsuji | 3 | `lua/kunio_route_tatsuji_targets.lua` | `lua/kunio_manual_route_tatsuji_capture_watch.lua` | `0x048F4, 0x052A5, 0x05BE5` |
| 3 | Heishichi | 3 | `lua/kunio_route_heishichi_targets.lua` | `lua/kunio_manual_route_heishichi_capture_watch.lua` | `0x06294, 0x0631B, 0x06359` |

## Rule

- Run these watchers on the base Japanese ROM.
- Press `D` only after manually reaching the matching route screen.
- The watcher overlay names the active route; if you only see the title/opening screen, switch screens instead of waiting.
- Use `python scripts/analyze_broad_scan_manual_dump.py` after capture.
- A route hit is still not patch approval unless the visible screen context matches.

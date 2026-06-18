# Katana Inventory Slot Candidates

This ranks the addresses from the failed temporary-state probe so the next run can be narrower.

## Summary

- Probed addresses: **19**
- Completed single-slot probes: 0x0502, 0x0503
- Recommended next probe: Try one candidate_small_probe address at a time. Completed probes did not show the Katana label; continue with 0x0506.

| classification | count |
| --- | ---: |
| `candidate_small_probe` | 5 |
| `defer_runtime_state` | 8 |
| `defer_unknown_state` | 3 |
| `exclude_menu_state` | 3 |

## Address Rows

| address | domain | menu | item list | changed | classification | reason |
| --- | --- | --- | --- | --- | --- | --- |
| `0x0502` | cpu | `0x04` | `0x3C` | true | `candidate_small_probe` | Small CPU state area that changed without being direct nametable data. |
| `0x0503` | cpu | `0x06` | `0x3E` | true | `candidate_small_probe` | Small CPU state area that changed without being direct nametable data. |
| `0x0506` | cpu | `0x07` | `0x01` | true | `candidate_small_probe` | Small CPU state area that changed without being direct nametable data. |
| `0x0508` | cpu | `0x9C` | `0x9C` | false | `candidate_small_probe` | Small CPU state area that changed without being direct nametable data. |
| `0x0509` | cpu | `0xD9` | `0x42` | true | `candidate_small_probe` | Small CPU state area that changed without being direct nametable data. |
| `0x0700` | cpu | `0x80` | `0x82` | true | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x0701` | cpu | `0x00` | `0x0C` | true | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x0702` | cpu | `0x00` | `0x0C` | true | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x0706` | cpu | `0x03` | `0x00` | true | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x0707` | cpu | `0x00` | `0x6E` | true | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x071D` | cpu | `0x00` | `0x00` | false | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x071E` | cpu | `0x00` | `0x00` | false | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x071F` | cpu | `0x00` | `0x01` | true | `defer_runtime_state` | CPU runtime state differs by menu screen; may affect control flow. |
| `0x7700` | sram | `0x01` | `0x00` | true | `exclude_menu_state` | Observed route/menu-control bytes, not stable item-slot storage. |
| `0x7701` | sram | `0x06` | `0x05` | true | `exclude_menu_state` | Observed route/menu-control bytes, not stable item-slot storage. |
| `0x7705` | sram | `0x10` | `0x00` | true | `exclude_menu_state` | Observed route/menu-control bytes, not stable item-slot storage. |
| `0x7720` | sram | `0x06` | `0x06` | false | `defer_unknown_state` | Nearby state changed during menu transitions; test only after narrower evidence. |
| `0x7721` | sram | `0xFE` | `0xFE` | false | `defer_unknown_state` | Nearby state changed during menu transitions; test only after narrower evidence. |
| `0x7722` | sram | `0x01` | `0x01` | false | `defer_unknown_state` | Nearby state changed during menu transitions; test only after narrower evidence. |

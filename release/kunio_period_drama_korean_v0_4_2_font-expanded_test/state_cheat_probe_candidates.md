# State Cheat Probe Candidates

This report ranks CPU RAM addresses that change across existing route/dialogue/menu captures.
It is meant to narrow the next FCEUX Lua cheat search for scene warps, enemy-clear flags, and boss-spawn state.

## Summary

- Snapshots compared: **28**
- Candidate addresses: **724**
- Top candidates shown: **32**
- Recommended use: Use these addresses as the first watch/write candidates for route cheats, not as confirmed cheat codes.

## Sources

| group | folder | CPU RAM snapshots |
| --- | --- | ---: |
| `input_dialogue` | `rom_analysis/fceux_input_explorer_v042` | 4 |
| `katana_menu_route` | `rom_analysis/katana_visual_explorer_v042` | 24 |

## Top RAM Candidates

| address | role | score | unique | changes | separates groups | late values | values by group |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `0x00E7` | `zero_page_engine_state` | 54 | 26 | 26 | false | input_dialogue=0x32, katana_menu_route=0x9A | input_dialogue=29 32 42 59, katana_menu_route=05 1F 25 40 42 47 59 5B 63 69 6E 7F 8E 9A 9C A2 A8 AE AF BA C3 EC F0 F8 |
| `0x002A` | `zero_page_engine_state` | 43 | 17 | 24 | false | input_dialogue=0x5D, katana_menu_route=0x31 | input_dialogue=3A 5D 5F, katana_menu_route=00 06 1B 2A 31 35 3A 3E 4C 4D 50 5D 5F 62 70 91 AB |
| `0x002C` | `zero_page_engine_state` | 43 | 17 | 24 | false | input_dialogue=0xEF, katana_menu_route=0x89 | input_dialogue=92 EF F9, katana_menu_route=00 1D 2B 31 36 47 50 79 89 92 94 C2 C7 D7 E1 EF F9 |
| `0x001F` | `zero_page_engine_state` | 40 | 15 | 23 | false | input_dialogue=0x1D, katana_menu_route=0x80 | input_dialogue=1D 67 77 E1, katana_menu_route=05 56 60 61 67 77 80 81 D0 D5 DC EC FA |
| `0x002D` | `zero_page_engine_state` | 37 | 14 | 21 | false | input_dialogue=0x92, katana_menu_route=0xD3 | input_dialogue=07 92, katana_menu_route=00 07 20 25 6B 80 8B 8E 90 92 B1 BA D3 D4 |
| `0x001C` | `zero_page_engine_state` | 35 | 11 | 22 | false | input_dialogue=0x19, katana_menu_route=0x00 | input_dialogue=19 73 C0 DC, katana_menu_route=00 4E 51 64 73 85 C0 D1 DC F6 |
| `0x0020` | `zero_page_engine_state` | 34 | 11 | 21 | false | input_dialogue=0x88, katana_menu_route=0x80 | input_dialogue=02 7F 88, katana_menu_route=02 06 0A 30 78 7F 80 88 89 98 D0 |
| `0x0720` | `runtime_flags` | 34 | 13 | 19 | false | input_dialogue=0xB1, katana_menu_route=0x69 | input_dialogue=00 0E 20 B1, katana_menu_route=00 0E 0F 15 23 56 69 70 81 C4 F3 |
| `0x0721` | `runtime_flags` | 34 | 13 | 19 | false | input_dialogue=0x45, katana_menu_route=0x50 | input_dialogue=00 20 45 95, katana_menu_route=00 1D 23 26 50 52 95 96 9E F2 F4 |
| `0x0722` | `runtime_flags` | 34 | 13 | 19 | false | input_dialogue=0xC9, katana_menu_route=0x5B | input_dialogue=00 12 20 C9, katana_menu_route=00 0F 10 12 14 1C 23 55 5B 65 AC |
| `0x0723` | `runtime_flags` | 34 | 13 | 19 | false | input_dialogue=0x7A, katana_menu_route=0x3E | input_dialogue=00 6B 72 7A, katana_menu_route=00 39 3E 40 6C 72 73 7B 95 97 CC |
| `0x001A` | `zero_page_engine_state` | 33 | 11 | 20 | false | input_dialogue=0x90, katana_menu_route=0x80 | input_dialogue=14 90, katana_menu_route=00 01 02 03 10 14 28 80 90 A9 E0 |
| `0x002B` | `zero_page_engine_state` | 33 | 11 | 20 | false | input_dialogue=0x89, katana_menu_route=0x01 | input_dialogue=89 E2, katana_menu_route=00 01 02 07 77 87 88 89 91 C3 E2 |
| `0x0084` | `zero_page_engine_state` | 33 | 12 | 19 | false | input_dialogue=0xED, katana_menu_route=0x31 | input_dialogue=00 47 B0 ED, katana_menu_route=00 25 28 31 47 80 A5 C0 CA E0 |
| `0x0002` | `zero_page_engine_state` | 32 | 9 | 21 | false | input_dialogue=0x3A, katana_menu_route=0x35 | input_dialogue=00 31 3A 52, katana_menu_route=00 31 34 35 36 38 52 98 |
| `0x0708` | `runtime_flags` | 31 | 12 | 17 | false | input_dialogue=0x72, katana_menu_route=0x8C | input_dialogue=00 42 72 BD, katana_menu_route=00 1E 34 42 4C 54 5C 8C A2 C3 |
| `0x07A9` | `runtime_flags` | 30 | 11 | 17 | false | input_dialogue=0x0C, katana_menu_route=0x1A | input_dialogue=00 0C 20, katana_menu_route=00 17 1A 1B 1C 1E 21 64 8C |
| `0x0009` | `zero_page_engine_state` | 29 | 8 | 19 | false | input_dialogue=0x00, katana_menu_route=0x00 | input_dialogue=00 80, katana_menu_route=00 04 10 20 40 80 E7 F3 |
| `0x0013` | `zero_page_engine_state` | 29 | 12 | 15 | false | input_dialogue=0x1D, katana_menu_route=0x00 | input_dialogue=00 1D 77 E1, katana_menu_route=00 56 60 77 78 81 D0 D5 DC EC |
| `0x001D` | `zero_page_engine_state` | 29 | 7 | 20 | false | input_dialogue=0x00, katana_menu_route=0x00 | input_dialogue=00 67, katana_menu_route=00 01 03 04 63 67 FF |
| `0x002F` | `zero_page_engine_state` | 29 | 9 | 18 | false | input_dialogue=0x08, katana_menu_route=0x01 | input_dialogue=00 08, katana_menu_route=00 01 07 08 10 12 17 60 FF |
| `0x00FC` | `zero_page_engine_state` | 29 | 9 | 18 | false | input_dialogue=0x03, katana_menu_route=0x05 | input_dialogue=03 09, katana_menu_route=03 05 07 09 0B 0D 5F 61 6B |
| `0x07A8` | `runtime_flags` | 29 | 10 | 17 | false | input_dialogue=0xE4, katana_menu_route=0x78 | input_dialogue=00 20 E4, katana_menu_route=00 17 1F 21 64 78 8C B4 |
| `0x07C3` | `runtime_flags` | 29 | 10 | 17 | false | input_dialogue=0xFA, katana_menu_route=0x35 | input_dialogue=00 F0 F1 FA, katana_menu_route=00 31 35 36 38 F0 F1 F4 F6 |
| `0x0000` | `zero_page_engine_state` | 28 | 7 | 19 | false | input_dialogue=0x72, katana_menu_route=0x72 | input_dialogue=00 72 95, katana_menu_route=00 2B 72 95 A9 BE E4 |
| `0x0001` | `zero_page_engine_state` | 28 | 7 | 19 | false | input_dialogue=0xAE, katana_menu_route=0xAE | input_dialogue=00 AE B9, katana_menu_route=00 9E AE B2 B7 B8 B9 |
| `0x0003` | `zero_page_engine_state` | 28 | 6 | 20 | false | input_dialogue=0x5D, katana_menu_route=0x65 | input_dialogue=00 5D 84, katana_menu_route=00 5D 65 80 84 85 |
| `0x002E` | `zero_page_engine_state` | 28 | 9 | 17 | false | input_dialogue=0x00, katana_menu_route=0x01 | input_dialogue=00, katana_menu_route=00 01 1C 4D 63 72 A8 D4 FF |
| `0x00F8` | `zero_page_engine_state` | 28 | 4 | 22 | false | input_dialogue=0x8C, katana_menu_route=0x88 | input_dialogue=88 8C, katana_menu_route=08 0C 88 8C |
| `0x073B` | `runtime_flags` | 28 | 9 | 17 | false | input_dialogue=0x1F, katana_menu_route=0x29 | input_dialogue=00 1F 24 26, katana_menu_route=00 18 1D 1F 20 24 26 29 2B |
| `0x07BB` | `runtime_flags` | 28 | 9 | 17 | false | input_dialogue=0x1D, katana_menu_route=0x26 | input_dialogue=00 1D 1F, katana_menu_route=00 15 1D 22 23 25 26 27 |
| `0x07C5` | `runtime_flags` | 28 | 9 | 17 | false | input_dialogue=0x58, katana_menu_route=0xC1 | input_dialogue=00 04 58 E5, katana_menu_route=00 03 04 44 58 82 AC C1 E5 |

## Next Probe

Build a Lua script that watches the top zero-page/object/runtime candidates while entering, leaving, or forcing route screens.
Avoid broad writes. Write one suspected state byte at a time and capture both CPU records and a screenshot.

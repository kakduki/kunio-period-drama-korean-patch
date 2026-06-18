# Object State Probe Candidates

This report filters the state-cheat scan to CPU RAM `$0300-$04FF`, the likely object/enemy/route-state area.
Use it for boss-spawn or enemy-clear cheat discovery before trying more isolated runtime-flag writes.

## Summary

- Snapshots compared: **28**
- Object range: `0x0300-0x04FF`
- Candidate addresses: **68**
- Top candidates shown: **32**
- Recommended use: Probe these before more runtime-flag writes; they are more likely to represent actors, enemies, route objects, or spawn state.

## Top Object/Enemy Candidates

| address | slot hint | score | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `0x04FA` | `block=1F column=A` | 22 | 6 | 14 | input_dialogue=0x30, katana_menu_route=0x42 | input_dialogue=30 3C, katana_menu_route=30 3C 42 5C 5E 68 |
| `0x04FB` | `block=1F column=B` | 21 | 6 | 13 | input_dialogue=0x31, katana_menu_route=0x47 | input_dialogue=31 3D, katana_menu_route=31 3D 47 5D 5F 69 |
| `0x04FC` | `block=1F column=C` | 21 | 6 | 13 | input_dialogue=0x32, katana_menu_route=0x35 | input_dialogue=32 3E, katana_menu_route=32 35 3E 5E 60 6A |
| `0x04FD` | `block=1F column=D` | 21 | 6 | 13 | input_dialogue=0x33, katana_menu_route=0x40 | input_dialogue=33 3F, katana_menu_route=33 3F 40 5F 61 6B |
| `0x04F1` | `block=1F column=1` | 20 | 4 | 14 | input_dialogue=0x02, katana_menu_route=0x01 | input_dialogue=02 12, katana_menu_route=00 01 02 12 |
| `0x04F3` | `block=1F column=3` | 18 | 3 | 13 | input_dialogue=0xFF, katana_menu_route=0x01 | input_dialogue=12 FF, katana_menu_route=01 12 FF |
| `0x04F4` | `block=1F column=4` | 18 | 3 | 13 | input_dialogue=0xFF, katana_menu_route=0x00 | input_dialogue=14 FF, katana_menu_route=00 14 FF |
| `0x04F2` | `block=1F column=2` | 16 | 4 | 10 | input_dialogue=0x15, katana_menu_route=0x00 | input_dialogue=14 15, katana_menu_route=00 13 14 15 |
| `0x031D` | `block=01 column=D` | 7 | 2 | 3 | input_dialogue=0x40, katana_menu_route=0x00 | input_dialogue=00 40, katana_menu_route=00 40 |
| `0x031E` | `block=01 column=E` | 7 | 2 | 3 | input_dialogue=0x40, katana_menu_route=0x00 | input_dialogue=00 40, katana_menu_route=00 40 |
| `0x0325` | `block=02 column=5` | 7 | 2 | 3 | input_dialogue=0xFF, katana_menu_route=0x00 | input_dialogue=00 FF, katana_menu_route=00 FF |
| `0x0326` | `block=02 column=6` | 7 | 2 | 3 | input_dialogue=0xFF, katana_menu_route=0x00 | input_dialogue=00 FF, katana_menu_route=00 FF |
| `0x039E` | `block=09 column=E` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x0B | input_dialogue=00, katana_menu_route=00 01 0B |
| `0x039F` | `block=09 column=F` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x03 | input_dialogue=00, katana_menu_route=00 01 03 |
| `0x03DB` | `block=0D column=B` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xF3 | input_dialogue=00, katana_menu_route=00 F3 F9 |
| `0x03DF` | `block=0D column=F` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x57 | input_dialogue=00, katana_menu_route=00 57 60 |
| `0x03E0` | `block=0E column=0` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xB7 | input_dialogue=00, katana_menu_route=00 B7 C0 |
| `0x03E1` | `block=0E column=1` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x0D | input_dialogue=00, katana_menu_route=00 07 0D |
| `0x03E6` | `block=0E column=6` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x64 | input_dialogue=00, katana_menu_route=00 64 67 |
| `0x03E7` | `block=0E column=7` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xC4 | input_dialogue=00, katana_menu_route=00 C4 C7 |
| `0x03FA` | `block=0F column=A` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x21 | input_dialogue=00, katana_menu_route=00 18 21 |
| `0x03FB` | `block=0F column=B` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x21 | input_dialogue=00, katana_menu_route=00 18 21 |
| `0x03FC` | `block=0F column=C` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x21 | input_dialogue=00, katana_menu_route=00 18 21 |
| `0x0401` | `block=10 column=1` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x1C | input_dialogue=00, katana_menu_route=00 18 1C |
| `0x0402` | `block=10 column=2` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x1C | input_dialogue=00, katana_menu_route=00 18 1C |
| `0x0403` | `block=10 column=3` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x1C | input_dialogue=00, katana_menu_route=00 18 1C |
| `0x042F` | `block=12 column=F` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x12 | input_dialogue=00, katana_menu_route=00 07 12 |
| `0x0432` | `block=13 column=2` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xA0 | input_dialogue=00, katana_menu_route=00 97 A0 |
| `0x0434` | `block=13 column=4` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x6A | input_dialogue=00, katana_menu_route=00 58 6A |
| `0x0435` | `block=13 column=5` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x12 | input_dialogue=00, katana_menu_route=00 07 12 |
| `0x0439` | `block=13 column=9` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x9B | input_dialogue=00, katana_menu_route=00 97 9B |
| `0x043A` | `block=13 column=A` | 7 | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x80 | input_dialogue=00, katana_menu_route=00 7F 80 |

## Next Probe

Test one address and one value at a time with `lua/kunio_state_single_byte_probe.lua`.
Prefer late `input_dialogue` values when trying to reproduce dialogue-like screens, but keep selected PNG evidence only when a visible state changes.

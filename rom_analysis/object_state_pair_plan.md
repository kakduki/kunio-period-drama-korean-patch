# Object State Pair Plan

This groups changing `$0300-$04FF` addresses into 16-byte object/state blocks.
The goal is to avoid wasting runs on adjacent single-byte writes when the game likely stores actor state across several fields.

## Summary

- Snapshots compared: **28**
- Object range: `0x0300-0x04FF`
- Candidate blocks: **21**
- Top blocks shown: **12**
- Recommended use: Use the recommended fields as a small paired-write queue; do not treat any block as confirmed until screenshots and target records change.

## Block 0x04F0

- Score: **141**
- Changing fields: **8**
- Recommended paired probe:
  - `0x04FA = 0x30`
  - `0x04F1 = 0x02`
  - `0x04FB = 0x31`
  - `0x04FC = 0x32`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x04FA` | `0xA` | 6 | 14 | input_dialogue=0x30, katana_menu_route=0x42 | input_dialogue=30 3C, katana_menu_route=30 3C 42 5C 5E 68 |
| `0x04F1` | `0x1` | 4 | 14 | input_dialogue=0x02, katana_menu_route=0x01 | input_dialogue=02 12, katana_menu_route=00 01 02 12 |
| `0x04FB` | `0xB` | 6 | 13 | input_dialogue=0x31, katana_menu_route=0x47 | input_dialogue=31 3D, katana_menu_route=31 3D 47 5D 5F 69 |
| `0x04FC` | `0xC` | 6 | 13 | input_dialogue=0x32, katana_menu_route=0x35 | input_dialogue=32 3E, katana_menu_route=32 35 3E 5E 60 6A |

## Block 0x0430

- Score: **33**
- Changing fields: **7**
- Recommended paired probe:
  - `0x0432 = 0x00`
  - `0x0434 = 0x00`
  - `0x0435 = 0x00`
  - `0x0439 = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x0432` | `0x2` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xA0 | input_dialogue=00, katana_menu_route=00 97 A0 |
| `0x0434` | `0x4` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x6A | input_dialogue=00, katana_menu_route=00 58 6A |
| `0x0435` | `0x5` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x12 | input_dialogue=00, katana_menu_route=00 07 12 |
| `0x0439` | `0x9` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x9B | input_dialogue=00, katana_menu_route=00 97 9B |

## Block 0x03E0

- Score: **23**
- Changing fields: **5**
- Recommended paired probe:
  - `0x03E0 = 0x00`
  - `0x03E1 = 0x00`
  - `0x03E6 = 0x00`
  - `0x03E7 = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x03E0` | `0x0` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xB7 | input_dialogue=00, katana_menu_route=00 B7 C0 |
| `0x03E1` | `0x1` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x0D | input_dialogue=00, katana_menu_route=00 07 0D |
| `0x03E6` | `0x6` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x64 | input_dialogue=00, katana_menu_route=00 64 67 |
| `0x03E7` | `0x7` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xC4 | input_dialogue=00, katana_menu_route=00 C4 C7 |

## Block 0x03F0

- Score: **21**
- Changing fields: **5**
- Recommended paired probe:
  - `0x03FA = 0x00`
  - `0x03FB = 0x00`
  - `0x03FC = 0x00`
  - `0x03F7 = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x03FA` | `0xA` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x21 | input_dialogue=00, katana_menu_route=00 18 21 |
| `0x03FB` | `0xB` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x21 | input_dialogue=00, katana_menu_route=00 18 21 |
| `0x03FC` | `0xC` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x21 | input_dialogue=00, katana_menu_route=00 18 21 |
| `0x03F7` | `0x7` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x05 | input_dialogue=00, katana_menu_route=00 05 |

## Block 0x0360

- Score: **15**
- Changing fields: **5**
- Recommended paired probe:
  - `0x0364 = 0x00`
  - `0x0365 = 0x00`
  - `0x0368 = 0x00`
  - `0x0369 = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x0364` | `0x4` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x01 | input_dialogue=00, katana_menu_route=00 01 |
| `0x0365` | `0x5` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x01 | input_dialogue=00, katana_menu_route=00 01 |
| `0x0368` | `0x8` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x01 | input_dialogue=00, katana_menu_route=00 01 |
| `0x0369` | `0x9` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x01 | input_dialogue=00, katana_menu_route=00 01 |

## Block 0x0370

- Score: **15**
- Changing fields: **5**
- Recommended paired probe:
  - `0x0379 = 0x00`
  - `0x037A = 0x00`
  - `0x037B = 0x00`
  - `0x037C = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x0379` | `0x9` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x93 | input_dialogue=00, katana_menu_route=00 93 |
| `0x037A` | `0xA` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x8F | input_dialogue=00, katana_menu_route=00 8F |
| `0x037B` | `0xB` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x80 | input_dialogue=00, katana_menu_route=00 80 |
| `0x037C` | `0xC` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x80 | input_dialogue=00, katana_menu_route=00 80 |

## Block 0x0400

- Score: **15**
- Changing fields: **3**
- Recommended paired probe:
  - `0x0401 = 0x00`
  - `0x0402 = 0x00`
  - `0x0403 = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x0401` | `0x1` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x1C | input_dialogue=00, katana_menu_route=00 18 1C |
| `0x0402` | `0x2` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x1C | input_dialogue=00, katana_menu_route=00 18 1C |
| `0x0403` | `0x3` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x1C | input_dialogue=00, katana_menu_route=00 18 1C |

## Block 0x0310

- Score: **13**
- Changing fields: **3**
- Recommended paired probe:
  - `0x031D = 0x40`
  - `0x031E = 0x40`
  - `0x0310 = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x031D` | `0xD` | 2 | 3 | input_dialogue=0x40, katana_menu_route=0x00 | input_dialogue=00 40, katana_menu_route=00 40 |
| `0x031E` | `0xE` | 2 | 3 | input_dialogue=0x40, katana_menu_route=0x00 | input_dialogue=00 40, katana_menu_route=00 40 |
| `0x0310` | `0x0` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x60 | input_dialogue=00, katana_menu_route=00 60 |

## Block 0x03D0

- Score: **13**
- Changing fields: **3**
- Recommended paired probe:
  - `0x03DB = 0x00`
  - `0x03DF = 0x00`
  - `0x03DE = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x03DB` | `0xB` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0xF3 | input_dialogue=00, katana_menu_route=00 F3 F9 |
| `0x03DF` | `0xF` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x57 | input_dialogue=00, katana_menu_route=00 57 60 |
| `0x03DE` | `0xE` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x7F | input_dialogue=00, katana_menu_route=00 7F |

## Block 0x0320

- Score: **10**
- Changing fields: **2**
- Recommended paired probe:
  - `0x0325 = 0xFF`
  - `0x0326 = 0xFF`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x0325` | `0x5` | 2 | 3 | input_dialogue=0xFF, katana_menu_route=0x00 | input_dialogue=00 FF, katana_menu_route=00 FF |
| `0x0326` | `0x6` | 2 | 3 | input_dialogue=0xFF, katana_menu_route=0x00 | input_dialogue=00 FF, katana_menu_route=00 FF |

## Block 0x0390

- Score: **10**
- Changing fields: **2**
- Recommended paired probe:
  - `0x039E = 0x00`
  - `0x039F = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x039E` | `0xE` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x0B | input_dialogue=00, katana_menu_route=00 01 0B |
| `0x039F` | `0xF` | 3 | 2 | input_dialogue=0x00, katana_menu_route=0x03 | input_dialogue=00, katana_menu_route=00 01 03 |

## Block 0x0300

- Score: **9**
- Changing fields: **3**
- Recommended paired probe:
  - `0x0304 = 0x00`
  - `0x0305 = 0x00`
  - `0x030F = 0x00`

| address | column | unique | changes | late values | values by group |
| --- | --- | ---: | ---: | --- | --- |
| `0x0304` | `0x4` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x80 | input_dialogue=00, katana_menu_route=00 80 |
| `0x0305` | `0x5` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x80 | input_dialogue=00, katana_menu_route=00 80 |
| `0x030F` | `0xF` | 2 | 1 | input_dialogue=0x00, katana_menu_route=0x40 | input_dialogue=00, katana_menu_route=00 40 |

## Next Probe

Add a paired-write Lua mode or run a tiny custom Lua probe for the top block only.
Start with block `0x04F0` because `$04FA` and `$04FB` were individually tested, then write the recommended block values together if single-byte tests remain unhelpful.

# Build Matrix

This matrix tracks development candidates, not release builds.
Historical opening proof remains recorded while the main menu is added as a
separate renderer family.

| build | ROM offset / PRG bank | English-reference check | bounded runtime | visual | result |
| --- | --- | --- | --- | --- | --- |
| opening_ptr_182_16x16_readability_proof | `0x071B6` / Bank 1 | source-slot structure checked | pointer 182 PASS | PASS | HISTORICAL_BASELINE |
| opening_ptr_182_183_16x16_readability | `0x071B6`, `0x071D7` / Bank 1 | pointer relocation checked | 182 `33/33`; 183 `25/25` | PASS | SUPERSEDED_BY_THREE_RECORD_CANDIDATE |
| opening_ptr_182_184_16x16_readability | `0x071B6`, `0x071D6`, `0x071EF` / Bank 1 | pointer range, source-slot, CHR, and relocation structure checked | 182 `32/32`; 183 `25/25`; 184 `23/23`; all `lua_done` | PASS on all three native screens | PASS_FOR_THREE_OPENING_CONTEXTS |
| main_menu_korean_16x16_candidate | `0x1F2C1` / Bank 7 | English slot layout and Bank 7 page evidence | frame 1906 `lua_done` | PASS | SOFT_GATE_PASS |

The current menu candidate is MD5 `de688d4bf18760cc4fa0682fee5571df` and uses cloned R1 page `0x46`.
Release verdict remains `UNKNOWN` until shared-raster contexts and menu lifecycle are checked.

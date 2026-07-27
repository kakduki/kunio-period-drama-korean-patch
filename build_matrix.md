# Build Matrix

This matrix tracks development candidates, not release builds.
Historical opening proof remains recorded while the main menu is added as a
separate renderer family.

| build | ROM offset / PRG bank | English-reference check | bounded runtime | visual | result |
| --- | --- | --- | --- | --- | --- |
| opening_ptr_182_16x16_readability_proof | `0x071B6` / Bank 1 | source-slot structure checked | pointer 182 PASS | PASS | HISTORICAL_BASELINE |
| opening_ptr_182_183_16x16_readability | `0x071B6`, `0x071D7` / Bank 1 | pointer relocation checked | 182 `33/33`; 183 `25/25` | PASS | SUPERSEDED_BY_THREE_RECORD_CANDIDATE |
| opening_ptr_182_184_16x16_readability | `0x071B6`, `0x071D6`, `0x071EF` / Bank 1 | pointer range, source-slot, CHR, and relocation structure checked | 182 `32/32`; 183 `25/25`; 184 `23/23`; all `lua_done` | PASS on all three native screens | PASS_FOR_THREE_OPENING_CONTEXTS |
| main_menu_korean_16x16_candidate | `0x1F2C1` / Bank 7 | English slot layout and Bank 7 page evidence | menu frame 1906 PASS; Items frame 1960 proves isolated pool | PASS menu / PASS page isolation | SOFT_GATE_PASS_ISOLATED_R1_POOL |
| korean_development_candidate | opening records + menu clone / Bank 1 + Bank 7 | complete 248-row pointer catalog; scoped opening/menu changes | p182 `32/32`; p183 `25/25`; p184 `23/23`; all `lua_done` | opening regression PASS; menu and Items isolation PASS | SOFT_GATE_PASS_COMBINED_CANDIDATE |
| pointer_dialogue_batch_002_003 | `0x06014`, relocated `0x06021` / Bank 1 | English pointer ownership and source-slot subset checked | boot PASS; opening route UNKNOWN; extended route phase 3/266 reads, target UNKNOWN | UNKNOWN; screen fingerprint stabilized, no manual screen claim | CANDIDATE_BUILT_RUNTIME_UNKNOWN |
| pointer_dialogue_batch_000_002_8x16 | `0x05FE7-0x0601A`, relocated p1/p2 / Bank 1 | English pointer ownership, source-slot subset, and protected p3 boundary checked | boot PASS at frame 883; bounded route frame 5000, phase 3/216 hits, target UNKNOWN | Font preview only; no native target capture | CANDIDATE_BUILT_RUNTIME_UNKNOWN |
| opening_ptr_182_16x16_capacity_tier2 | `0x071B6` / Bank 1; helper `0x07FB5` | 26 English slots plus bounded `0xC0-0xC7` extension | frame 883: `37/37` reads; `lua_done`; `70` emitted tile writes | Native screenshot PASS; no visible opening damage | SOFT_GATE_PASS_OPENING_CAPACITY_RUNTIME_AND_VISUAL |
| opening_dialogue_bank8_static_r1_page_proof | normal mapper setup `0x1EE57`; R1 `3E -> 46` | 7-glyph cloned-page ownership checked | frame 883 `18/18`; `lua_done`; mapping `28/28` | Native opening screenshot PASS | SOFT_GATE_PASS_PAGE_LIFECYCLE |
| opening_dialogue_bank8_static_r1_capacity_tier2 | normal mapper setup `0x1EE57`; R1 `3E -> 46` | 34 glyphs emit from Bank 8 but declared targets remain Bank 7 | frame 883 `37/37`; `lua_done`; mapping FAIL | Dialogue-only capture; background lost | FAIL_PAGE_SLOT_CONFLICT |

The current menu candidate is MD5 `d425814e4f1249e2872c9eb09f7fb93d` and uses cloned R1 page `0x46`.
The Items action source `0x13727` reaches PPU `0x2363` through the shared R1 page.
The menu screenshot and Items page-isolation capture pass the development soft gate; other R1 contexts remain unaudited.

The pointer batch 002/003 candidate has MD5 `863c62ba178973ee1a96cc7971512149`.
The direct 8x16 p0/p1/p2 candidate has MD5 `ba3ef60856e1d2b5aa4dba40bcf1ff41`.
Both remain separate from the opening/menu candidate until a common renderer
guard and a non-opening target route are proven.

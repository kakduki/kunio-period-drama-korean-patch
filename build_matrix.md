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
| opening_dialogue_bank8_static_r1_page_proof | normal mapper setup `0x1EE57`; R1 `3E -> 46` | 7-glyph target ownership checked | frame 883 `18/18`; `lua_done`; mapping `28/28` | Dialogue-only black frame | FAIL_STATIC_R1_VISUAL_BACKGROUND |
| opening_dialogue_bank8_static_r1_capacity_tier2 | normal mapper setup `0x1EE57`; R1 `3E -> 46` | 34 glyphs emit from Bank 8 but declared targets remain Bank 7 | frame 883 `37/37`; `lua_done`; mapping FAIL | Dialogue-only capture; background lost | FAIL_PAGE_SLOT_CONFLICT |
| opening_dialogue_bank8_static_r1_safe_capacity_tier2 | normal mapper setup `0x1EE57`; R1 `3E -> 46`; actual R1 `0x800`-byte window clone | 34 glyphs declared at Bank 8 runtime slots; source Bank 7 preserved | frame 883 `37/37`; `lua_done`; mapping `67/67` | Native opening background and Korean-looking dialogue visible | SOFT_GATE_PASS_SAFE_STATIC_R1_CAPACITY |
| full_pointer_korean_candidate | pointers `0-247`; packed records `0x05FC4-0x06EB0` (end-exclusive); 48 appended CHR pages | all active records preserve English non-letter control skeletons; 14 token-sensitive records use explicit Korean segments; width audit max `20/24`; 244 rows reviewed; 4 excluded rows retain Japanese bytes | forced pointers 0/25/50/110/181 PASS across pages 10/14/39/30/41; state, R1, source, terminator PASS | Korean text pixels and field background PASS on all 5 samples | WHOLE_SCRIPT_RUNTIME_PASS_5_PAGES |

The current menu candidate is MD5 `d425814e4f1249e2872c9eb09f7fb93d` and uses cloned R1 page `0x46`.
The Items action source `0x13727` reaches PPU `0x2363` through the shared R1 page.
The menu screenshot and Items page-isolation capture pass the development soft gate; other R1 contexts remain unaudited.

The pointer batch 002/003 candidate has MD5 `863c62ba178973ee1a96cc7971512149`.
The direct 8x16 p0/p1/p2 candidate has MD5 `ba3ef60856e1d2b5aa4dba40bcf1ff41`.
Both remain separate from the opening/menu candidate until a common renderer
guard and a non-opening target route are proven.

The full pointer candidate supersedes those small batches as the current
whole-script development build. Its MD5 is
`7844f2d6f6a67e86e23b2f954d5ebf3c`. It compiles 244 Korean dialogue rows,
including 244 English-reference-reviewed rows, retains four excluded
Japanese records, and proves the optimized-page runtime path on five
representative pages. The forced harness is page/font evidence, not natural
event-control proof; no translation drafts remain; broad visual coverage remains open.


## Full-pointer progression evidence

| build | route | bounded result | release interpretation |
| --- | --- | --- | --- |
| full_pointer_progression_probe | full candidate MD5 `7844f2d6f6a67e86e23b2f954d5ebf3c`; optional `KUNIO_EXTRA_DIALOGUE_START=1` | frame 392 pointer dialogue; frame 757 page state restored; frame 915 combat entry; frames 1926/1986 interaction pointers 135/136; frame 7200 `lua_done` | `PASS_GAMEPLAY_ENTRY_PASS_INTERACTION_UNKNOWN_BOSS` |

The extra Start input is a route correction discovered by the bounded button
probe; it is not blind autoplay. The reached 1926/1986 screen is the interaction/shop route (`WELCOME` / `WHAT WOULD YOU LIKE`), not boss proof. Full release-wide visual coverage remains open.

## Current Composed Candidate (2026-08-01)

- ROM: `output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes`.
- Candidate MD5: `d062b19d23050cd4e148e22fbfff57b7`.
- Composition: 244 active pointer-dialogue rows plus the bounded 16x16 main-menu template and isolated source-page glyph slots.
- English IPS coverage audit: 3 records fully covered by same-offset ownership, 7 partial, 89 missing; this is structural coverage, not visual proof.
- Bounded smoke: `SOFT_GATE_PASS_MENU_AND_GAMEPLAY_ENTRY`; menu template and mirror match, final R1 is `0x3E`, progression reaches combat and late event screens, and `lua_done` is recorded.
- Pointer route probe: `UNKNOWN_TARGET_ROUTE_PROBE_ADDRESS_CONTRACT`; its old fixed-address target does not match the relocated full-pointer layout.
- Release status: `UNKNOWN`; this is a development candidate, not a final release ROM.

## Full Non-Pointer Candidate (2026-08-01)

- Candidate ROM: output/full_nonpointer_korean_candidate/kunio_period_drama_korean_full_nonpointer_candidate.nes.
- Candidate MD5: 18284402f073b91c09d05f52a16b9b9d.
- Composition: current full pointer/menu candidate plus two safe equal-length non-pointer PRG targets.
- Applied targets: runtime-confirmed rom_07227_candidate_84 and encoding-exact watch_rom_0569d_..._7a.
- Excluded targets: 41 targets requiring padding proof or only static/pointer-hypothesis evidence.
- Bounded progression: lua_done; entry screens, combat at frame 915, and late event-like screens at frames 1956/2046 captured.
- Automated smoke: PASS; exact non-pointer screen visual proof: UNKNOWN; release: NOT_READY.
- Detailed report: rom_analysis/full_nonpointer_korean_candidate.md and rom_analysis/full_nonpointer_korean_candidate_smoke.md.

## Effective Name-Table Source Probe (2026-08-01)

| build | effective source / glyph slots | PPU target | bounded result | visual | result |
| --- | --- | --- | --- | --- | --- |
| name_table_korean_candidate | 0x3FB32 empirical effective source table; CHR slots 0x2F820-0x2F850 | 0x2043-0x2046: 88969F8B -> 81828182 | 9 differential probes; only 0x3FB32 changed the live sequence | PASS, frame 1956 screenshot | SOFT_GATE_PASS_ONE_CONTEXT |

The English static occurrence at 0x0561B did not change the natural-route PPU sequence. The corrected candidate ROM MD5 is df586e888e23761d2da518162444810e. This proves one non-pointer renderer context with a bounded test string; it is not whole-game visual coverage and is not a release build.
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
## Full Pointer Sweep Audit (2026-08-01)

- Candidate ROM: output/full_korean_candidate/kunio_period_drama_korean_full_candidate.nes
- Candidate MD5: d062b19d23050cd4e148e22fbfff57b7
- Scope: 248 bounded forced-pointer runs, one pointer per run, 450 frames each.
- Active rows: 244/244 PASS.
- Excluded non-dialogue rows: 4/4 PASS.
- Source modes: 201 direct terminators, 41 control-stream/static terminators, 2 static terminators not reached by the watch.
- Every run captured text pixels and the preserved field background.
- Final mapper R1 was recorded only as a diagnostic; the page-aware renderer restores the normal mapper state before the final capture, so R1=3E is not a failure.
- Interpretation: whole-script pointer compilation and renderer/page handling pass the development soft gate. This is forced renderer evidence, not natural enemy-clear, boss-spawn, or release-wide visual proof.
- Detailed report: rom_analysis/full_pointer_sweep_runtime.md.
## Expanded Non-Pointer Candidate (2026-08-01)

- Candidate ROM: output/expanded_nonpointer_korean_candidate/kunio_period_drama_korean_expanded_nonpointer_candidate.nes
- Candidate MD5: 12baf49a9b08a0a93b7f2d0e3140289c
- Build: PASS; IPS round trip: PASS.
- Scope: 9 equal-length PRG targets selected from the real frame-883 target record set, plus 18 Korean 8x8 glyph slots copied from the existing font expansion.
- Bounded stage progression: PASS; the route reaches combat and late event-like captures and ends with lua_done.
- Exact changed-string screen proof: UNKNOWN. The current composed candidate route does not reproduce the old frame-883 input-explorer screen.
- Route comparison: both the current composed candidate and the expanded candidate reach only two unique screens in the 1000-frame input explorer run, then write a finite done row. This behavior predates the nine added targets and is not evidence that those targets caused the opening-screen loop.
- Release status: NOT_READY.
- Detailed build report: rom_analysis/expanded_nonpointer_korean_candidate.md.
## Legacy-Route Non-Pointer Candidate (2026-08-01)

- Candidate ROM: output/expanded_nonpointer_legacy_route_candidate/kunio_period_drama_korean_expanded_nonpointer_candidate.nes
- Base ROM MD5: 0d406a85285b4de8468f0dab6aad5fe5
- Candidate MD5: cc450f38b32dfeaa7864b4784874b6ed
- Scope: 9 equal-length PRG targets and 18 Korean 8x8 glyph slots.
- Bounded input route: frame 883 reached on the original English-compatible route.
- Exact target-record proof: 9/9 selected PRG targets have active_expected_match=true at frame 883.
- Capture directory: C:	mplegacy_nonpointer_input_explorer.
- The quarantined 0x07227 Katana target is intentionally not included.
- Soft-gate result: PASS for source ownership and bounded screen capture.
- Release status: NOT_READY; the candidate is a nine-string context build, not a whole-game Korean release.
## Input Explorer Default Transition (2026-08-01)

The input explorer now enables the known dialogue Start transition by default and accepts KUNIO_EXTRA_DIALOGUE_START=0 to disable it. On the current full candidate, the default bounded run recorded four unique screens at frames 121, 361, 655, and 906, then wrote a finite done row at frame 1000.

## Items Action Candidate (2026-08-01)

| build | ROM offset / PRG bank | English-reference check | bounded runtime | visual | result |
| --- | --- | --- | --- | --- | --- |
| full_korean_items_action_candidate | 0x13727 / PRG 16 KiB bank 4, MMC3 R7 0x09 | source 0x13727 -> CPU $B717 -> SRAM $6360 -> PPU $2363; static source and IPS checks PASS | FCEUX capture frame 1906, action row frame 1736; runtime verifier PASS | native GD screenshot blank; visual UNKNOWN | BUILT_STATIC_PASS_RUNTIME_PASS_VISUAL_UNKNOWN |

The candidate composes the full direct-low development candidate with four Items action
labels: 사용, 버리기, 주기, and 버림. It uses the normal Items R1 pages
0x3E/0x3F, so it is intentionally a development candidate until a candidate
screen capture proves that page's cross-context safety. KUNIO'S ITEMS and NONE
remain separate source owners.
## Items Title / NONE Development Candidate (2026-08-01)

| build | ROM offset / owner | English-reference check | bounded runtime | visual | result |
| --- | --- | --- | --- | --- | --- |
| full_korean_items_title_none_candidate | `0x0561B`, `0x3FB32`, `0x136F4`, `0x0FC31` / PRG + CHR15 | PRG/CHR duplicate name seed, dynamic title suffix, and direct-low NONE owner traced from English runtime | FCEUX capture frame 1906; name/title/NONE queue frame 1737 PASS; action queue/PPU preserved | UNKNOWN; native GD screenshot transparent | BUILT_RUNTIME_BYTE_PASS_VISUAL_UNKNOWN |

This candidate is the current bounded Items development build. It is not a release ROM: the byte path is proven, but native visual review and shared-page safety remain open.

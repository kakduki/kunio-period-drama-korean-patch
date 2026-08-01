# Main Menu Items Context

Context verdict: **PASS**
Shared-page candidate verdict: **PASS**
Release verdict: **UNKNOWN**

## Proven Chain

`0x13727` (PRG 16 KiB bank 4; MMC3 8 KiB bank 9)
-> CPU `0xB717`-`0xB737`
-> copy routine `0xB707`
-> SRAM `0x6360`
-> PPU `0x2363` action row.

The Japanese base and English reference both completed the same fixed 1,980-frame route with `lua_done`.
Their runtime source bytes matched ROM, their queue writes matched those source bytes, and their PPU action bytes matched the queue payload.

## English Reference

- Title: `KUNIO'S ITEMS` (row 5).
- Empty inventory: `NONE` (row 8).
- Action row: `USE, REMOVE, GIVE, DRP` (row 27).
- Korean action proposal: `사용 / 버리기 / 주기 / 버림`.

## Font Isolation

- Items low-code font page: `R0=0x3C`.
- Items action-code font page: `R1=0x3E`.
- Existing main-menu candidate: **PASS**. isolated Korean menu code pool is active without overlapping Items action codes

The bounded candidate keeps the original Items action bytes while the cloned R1 page is active.
The bounded title, empty-inventory, and action owners are now compiled in the development candidate below. Native visual evidence remains UNKNOWN because the available GD screenshot buffer is transparent.

## Checks

- `base_lua_done`: PASS
- `english_lua_done`: PASS
- `base_screen_available`: PASS
- `english_screen_available`: PASS
- `base_source_rom_offset`: PASS
- `english_source_rom_offset`: PASS
- `base_source_reads_match_rom`: PASS
- `english_source_reads_match_rom`: PASS
- `base_queue_matches_source`: PASS
- `english_queue_matches_source`: PASS
- `base_ppu_matches_action_bytes`: PASS
- `english_ppu_matches_action_bytes`: PASS
- `english_title_matches_reference`: PASS
- `english_none_matches_reference`: PASS
- `english_actions_match_reference`: PASS
- `base_r0_page_is_3c`: PASS
- `english_r0_page_is_3c`: PASS
- `base_r1_page_is_3e`: PASS
- `english_r1_page_is_3e`: PASS


## Action Candidate Follow-up (2026-08-01)

The static English source chain is now compiled into a separate development
candidate at rom_analysis/full_korean_items_action_candidate.md. The four
action labels are 사용, 버리기, 주기, and 버림, sourced from ROM
0x13727 and routed through CPU $B717, SRAM $6360, and PPU $2363.
The candidate's static scope and IPS round-trip pass. Its native FCEUX capture
is PASS; the relative-frame FCEUX capture ended lua_done and the runtime verifier matched source-derived queue/PPU bytes.
The generated GD screenshot is transparent blank, so this is runtime byte proof rather than manual visual approval.
In this action-only candidate they remain separate; the title/NONE candidate below now proves their byte path.
## Title / NONE Candidate (2026-08-01)

- Candidate ROM: `output/full_korean_items_title_none_candidate/kunio_period_drama_korean_full_items_title_none_candidate.nes`.
- Candidate MD5: `fa08179cdbf1198bd7781df0b6c78477`.
- Name owner: PRG `0x0561B` plus live CHR/PPU seed `0x3FB32` -> RAM `$7AFB` -> title prefix `$60A8`.
- Title suffix owner: PRG `0x136F4` -> RAM `$60AD`.
- NONE owner: PRG `0x0FC31` -> RAM `$6506`.
- FCEUX bounded route: capture frame `1906`; name/title/NONE queue proof at frame `1737`.
- Runtime byte gate: `PASS_BYTE_PROOF`.
- Native visual gate: `UNKNOWN`; screenshot buffer is transparent.
- Release status: `NOT_READY`.

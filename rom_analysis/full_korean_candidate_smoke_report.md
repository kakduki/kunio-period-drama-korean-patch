# Full Korean Candidate Smoke Report

Soft-gate status: **SOFT_GATE_PASS_MENU_AND_GAMEPLAY_ENTRY**
Release verdict: **UNKNOWN**

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `d062b19d23050cd4e148e22fbfff57b7`.
- Candidate ROM: `output\full_korean_candidate\kunio_period_drama_korean_full_candidate.nes`.
- Candidate IPS: `output\full_korean_candidate\kunio_period_drama_korean_full_candidate.ips`.

## Checks

- `base_md5`: PASS
- `candidate_chr_banks_expanded`: PASS
- `ips_round_trip`: PASS
- `menu_lua_done`: PASS
- `menu_template_display_matches`: PASS
- `menu_template_mirror_matches`: PASS
- `menu_r1_restored_original`: PASS
- `source_page_has_korean_changes`: PASS
- `progression_lua_done`: PASS
- `progression_reaches_combat`: PASS
- `progression_reaches_late_event`: PASS

## Evidence

- Menu capture: `rom_analysis\main_menu_full_korean_candidate_capture`.
- Progression capture: `rom_analysis\stage_progression_probe_full_korean_candidate`.
- Pointer route probe: `rom_analysis\pointer_dialogue_route_probe_full_korean_candidate`; interpretation is UNKNOWN because its fixed target address is stale.

## Limits

- This is a soft-gate development candidate, not a release ROM.
- The full 244-row script is compiled, but broad visual proof is not complete.
- The pointer route probe uses an older fixed-address target contract and returned UNKNOWN.
- The reached gameplay route does not prove boss defeat or every event screen.

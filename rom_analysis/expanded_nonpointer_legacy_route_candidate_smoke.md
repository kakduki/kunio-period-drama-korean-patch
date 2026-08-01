# Legacy-Route Non-Pointer Candidate Smoke

- Base ROM MD5: 0d406a85285b4de8468f0dab6aad5fe5
- Candidate ROM: output/expanded_nonpointer_legacy_route_candidate/kunio_period_drama_korean_expanded_nonpointer_candidate.nes
- Candidate MD5: cc450f38b32dfeaa7864b4784874b6ed
- Build status: PASS
- Bounded screen status: PASS
- Exact target-record status: PASS (9/9)
- Release status: NOT_READY

| check | result |
| --- | --- |
| candidate_exists | PASS |
| candidate_md5_matches_build | PASS |
| nine_equal_length_prg_targets | PASS |
| eighteen_korean_glyph_slots | PASS |
| input_route_reaches_frame_883 | PASS |
| selected_target_records_active | PASS (9/9) |
| quarantined_07227_excluded | PASS |
| whole_game_release | NOT_READY |

At frame 883 the legacy English-compatible input route produced active expected matches for all nine selected PRG targets:

- 0x0561A Hashi
- 0x0562F Tatsuichi
- 0x05643 Heishichi
- 0x0569D Hashi
- 0x056DA Hashi
- 0x0571C Hashi
- 0x057D4 Hashi
- 0x0736A Raifu
- 0x0739D Raifu

The capture files are in C:\tmp\legacy_nonpointer_input_explorer. The 0x07227 Katana target remains quarantined and is not patched. This is the first concrete nine-string screen-context candidate, but it is not a whole-game release.
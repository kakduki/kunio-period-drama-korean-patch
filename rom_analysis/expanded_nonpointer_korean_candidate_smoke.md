# Expanded Non-Pointer Candidate Smoke

- Candidate: output/expanded_nonpointer_korean_candidate/kunio_period_drama_korean_expanded_nonpointer_candidate.nes
- MD5: 12baf49a9b08a0a93b7f2d0e3140289c
- Build status: PASS
- IPS round trip: PASS
- Stage progression smoke: PASS
- Exact changed-string visual status: UNKNOWN
- Release status: NOT_READY

| check | result |
| --- | --- |
| candidate_exists | PASS |
| candidate_md5_matches_build | PASS |
| nine_equal_length_prg_targets | PASS |
| eighteen_korean_glyph_slots | PASS |
| ips_round_trip | PASS |
| bounded_stage_progression | PASS |
| fceux_lua_done | PASS |
| exact_frame_883_changed_string_capture | UNKNOWN |
| release_promotion | NOT_READY |

The bounded stage route reaches combat and late event-like captures and ends with lua_done. It does not reproduce the historical frame-883 input-explorer target screen on this current composed route.

A separate comparison ran the current composed candidate and this expanded candidate through the same 1000-frame input route. Both reached two unique screens and then wrote a finite done row. This behavior predates the nine added targets, so the opening-route issue is not attributed to those byte edits. The historical frame-883 target record set remains useful source evidence, but it is not exact visual proof for this candidate.
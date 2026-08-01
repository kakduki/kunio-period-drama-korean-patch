# Full Non-Pointer Korean Candidate Smoke

- Candidate: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\full_nonpointer_korean_candidate\kunio_period_drama_korean_full_nonpointer_candidate.nes
- MD5: 18284402f073b91c09d05f52a16b9b9d
- Automated status: PASS
- Visual status: UNKNOWN
- Release status: NOT READY

| check | result |
| --- | --- |
| candidate_exists | PASS |
| candidate_md5_matches_build | PASS |
| candidate_chr_expanded | PASS |
| build_applied_two_safe_targets | PASS |
| fceux_lua_done | PASS |
| entry_screen_captured | PASS |
| combat_screen_captured | PASS |
| late_event_screen_captured | PASS |

The bounded trace reaches lua_done, captures entry screens, reaches combat, and records late event-like screens.
This proves progression smoke only; it does not prove that the two changed strings are visible in their intended screen contexts.

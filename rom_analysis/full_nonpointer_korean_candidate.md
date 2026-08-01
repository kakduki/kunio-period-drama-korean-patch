# Full Non-Pointer Korean Candidate

This is a soft-gate development candidate composed on top of the full pointer/menu candidate.

- Base ROM: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes
- Input candidate: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\full_korean_candidate\kunio_period_drama_korean_full_candidate.nes
- Candidate ROM: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\full_nonpointer_korean_candidate\kunio_period_drama_korean_full_nonpointer_candidate.nes
- Candidate IPS: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\full_nonpointer_korean_candidate\kunio_period_drama_korean_full_nonpointer_candidate.ips
- Base MD5: 0d406a85285b4de8468f0dab6aad5fe5
- Candidate MD5: 18284402f073b91c09d05f52a16b9b9d
- Applied count: 2
- Skipped count: 41
- Changed bytes from clean base: 5523
- Build classification: PASS
- Release classification: UNKNOWN until exact screen visual proof and broader regression coverage.

## Applied

| label | ROM offset | source | Korean | old bytes | new bytes | evidence | risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rom_07227_candidate_84 | 0x07227 | カタナ | 카타나 | 8A 94 99 | 88 89 8A | runtime-confirmed | safe-equal-length |
| watch_rom_0569d_스테이지_7a | 0x0569D | はし | 다리 | A0 92 | 8B 8C | encoding-exact | safe-equal-length |

## Exclusion Summary

Targets requiring a padding rule or only static/pointer-hypothesis evidence remain excluded.

| reason | count |
| --- | ---: |
| evidence level 'static-candidate' not selected | 14 |
| evidence level 'static-candidate+pointer' not selected | 26 |
| patch risk 'needs-padding-rule' not selected | 1 |

## Gate

- Soft gate: PASS for deterministic build generation.
- Boot/progression smoke: run scripts/run_fceux_lua_analysis.py against the candidate.
- Visual proof: UNKNOWN until the two exact source contexts are captured.
- Release: NOT READY.

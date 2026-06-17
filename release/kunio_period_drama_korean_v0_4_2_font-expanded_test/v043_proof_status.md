# v0.4.3 Proof Status

This report joins the broad-scan proof packet, CPU-read summary, visual review file, and v0.4.3 build report.

## Summary

- Rows: **7**
- CPU-read matches: **0**
- Visual reviews confirmed: **0**
- Applied in v0.4.3 build: **0**
- Build verdict: `no candidate built; manual CPU-read and visual-context evidence is incomplete`

## Rows

| task | status | ROM | human hint | expected text | Korean | CPU read | visual | planned bytes | next action |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `needs_manual_capture` | `0x0440C` | blacksmith/stage label | かじや | 대장간 | no | no | `B5 93 AB` | Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context. |
| 2 | `needs_manual_capture` | `0x048F4` | boss/name label | たつじ | 타츠지 | no | no | `89 98 A1` | Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context. |
| 3 | `needs_manual_capture` | `0x052A5` | boss/name label | たつじ | 타츠지 | no | no | `89 98 A1` | Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context. |
| 4 | `needs_manual_capture` | `0x05BE5` | boss/name label | たつじ | 타츠지 | no | no | `89 98 A1` | Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context. |
| 5 | `needs_manual_capture` | `0x06294` | name/dialogue label | へいしち | 헤이시치 | no | no | `8D 8E 8F 90` | Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context. |
| 6 | `needs_manual_capture` | `0x0631B` | name/dialogue label | へいしち | 헤이시치 | no | no | `8D 8E 8F 90` | Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context. |
| 7 | `needs_manual_capture` | `0x06359` | name/dialogue label | へいしち | 헤이시치 | no | no | `8D 8E 8F 90` | Manually reach the target screen in the base ROM, run the broad-scan Lua dump, then review the screenshot/context. |

## Status Meaning

- `needs_manual_capture`: no CPU-read match and no visual confirmation yet.
- `needs_visual_review`: CPU bytes matched; confirm the visible screen before building.
- `needs_cpu_read_match`: visual review was marked, but the CPU-read proof is still missing.
- `ready_for_v043_builder`: both gates are satisfied; run the v0.4.3 builder.
- `applied`: the row was included in the generated v0.4.3 candidate.

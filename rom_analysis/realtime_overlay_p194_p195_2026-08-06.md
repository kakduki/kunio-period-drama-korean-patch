# Real-Time Overlay p194-p195 Runtime Evidence

Date: 2026-08-06

## Run

The verified Japanese base ROM was run with the bounded overlay emitter and the six-target table (p182-p185, p194-p195).

- Frame ceiling: 5000
- Registered source-read bytes: 158
- Event count: 9
- Lua summary: lua_done at frame 5000
- Output: C:\tmp\kunio_overlay_p194_p195_2026_08_06_v2

The wrapper reported a timeout while waiting for FCEUX to exit, but the copied Lua output contains the completion row and is therefore classified as a launcher-exit timeout, not an unbounded run.

## Reached events

| ID | Frames observed | Cache result |
| --- | --- | --- |
| OPENING-182 | 656 | CACHED |
| OPENING-183 | 718, 1047 | CACHED |
| OPENING-184 | 1349 | CACHED |
| OPENING-185 | 1655, 4565 | CACHED |
| OPENING-194 | 1671, 4517 | CACHED |
| OPENING-195 | 4857 | CACHED |

The overlay resolved p194 as Korean cached text for '나만 믿어' and p195 as Korean cached text for '부디 서둘러라'. No ROM or emulator memory was modified.

## Classification

PASS_SIX_TARGET_SIDECAR_WITH_LAUNCHER_EXIT_TIMEOUT

This proves sidecar event detection and cached Korean display for six verified opening/dialogue records. It does not promote p196/p197, prove the natural boss route, or replace native ROM visual gates.
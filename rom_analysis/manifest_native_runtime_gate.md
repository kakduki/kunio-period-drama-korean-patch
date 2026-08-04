# Manifest Candidate Native Runtime Gate

Date: 2026-08-05

## Current Four-Row Candidate

The selected manifest contains the reviewed opening rows p182 through p185. The
candidate was rebuilt from the verified Japanese base with the register-
preserving pointer loader.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `b6ae36bb14ac1ba0836e7d02204d4b57`
- Candidate SHA256: `dfdf6838663f26e933d63604398b028645622a5f3dc61074e2066239f07f21f7`
- Generated IPS MD5: `88ae9e0bf1b2d12a9dacfe73d4573b41`
- Candidate size: `368656` bytes
- Manifest updates/skips: `4` / `3`

| pointer | pointer ROM | candidate CPU | candidate ROM | bytes |
|---:|---:|---:|---:|---:|
| 182 | `0x05F40` | `$9FB4` | `0x05FC4` | 26 |
| 183 | `0x05F42` | `$9FCE` | `0x05FDE` | 14 |
| 184 | `0x05F44` | `$9FDC` | `0x05FEC` | 13 |
| 185 | `0x05F46` | `$9FE9` | `0x05FF9` | 11 |

The loader previously used `TAX/DEX` for the page-table index and corrupted the
caller's X register, producing a repeated `B6` dialogue-ID loop. It now uses
`TAY/DEY`; the helper remains exactly 64 bytes and the original dispatch
recomputes Y before reading the pointer table.

## Bounded Loader Trace

The trace consumes generated target definitions and is classified by
`scripts/analyze_manifest_loader_trace.py`:

```text
python scripts/generate_manifest_runtime_target.py --candidate C:\tmp\kunio_manifest_p182_p185_fourrow.nes --pointer-index 182 --pointer-index 183 --pointer-index 184 --pointer-index 185 --output C:\tmp\kunio_manifest_fourrow_targets.lua
python scripts/run_fceux_lua_analysis.py --rom C:\tmp\kunio_manifest_p182_p185_fourrow.nes --lua-script lua\kunio_manifest_loader_trace.lua --target-lua C:\tmp\kunio_manifest_fourrow_targets.lua --frames 1900 --timeout 60 --final-output C:\tmp\kunio_manifest_fourrow_loader_trace_v2 --clean-output --no-dump-hex --no-dump-bin
python scripts/analyze_manifest_loader_trace.py --trace C:\tmp\kunio_manifest_fourrow_loader_trace_v2 --candidate C:\tmp\kunio_manifest_p182_p185_fourrow.nes --pointer-index 182 --pointer-index 183 --pointer-index 184 --pointer-index 185 --json-out C:\tmp\kunio_manifest_fourrow_loader_trace_v2.json --markdown-out C:\tmp\kunio_manifest_fourrow_loader_trace_v2.md
```

- Analyzer status: `PASS`
- Completion: `lua_done` at frame `1900`
- Candidate record reads: `64` total (`26 + 14 + 13 + 11`)
- Dialogue ID progression includes `B7 -> B8 -> B9 -> BA -> BB`
- No repeated `B6` stall after the loader fix

## Native Visual Captures

Each target was generated from the candidate's own pointer table. The bounded
opening route was run separately for each target with no state writes:

| pointer | CPU | frame | hits | screenshot | target match | result |
|---:|---:|---:|---:|---|---|---|
| 182 | `$9FB4` | 712 | 26/26 | `true` | `true` | PASS |
| 183 | `$9FCE` | 1059 | 14/14 | `true` | `true` | PASS |
| 184 | `$9FDC` | 1345 | 13/13 | `true` | `true` | PASS |
| 185 | `$9FE9` | 1627 | 11/11 | `true` | `true` | PASS |

The individual summaries are kept in the external bounded output directories
`C:\tmp\kunio_fourrow_p182_visual` through `C:\tmp\kunio_fourrow_p185_visual`.

## Gate Classification

- Selected manifest rows p182-p185 native source-read gate: `PASS`.
- Selected manifest rows p182-p185 native visual capture gate: `PASS`.
- Full 248-row dialogue coverage: `UNKNOWN`.
- Non-pointer menus and dynamic contexts: `UNKNOWN`.
- Natural gameplay, event, and boss route: `UNKNOWN`.
- Release candidate: `NOT_READY`.

The four-row result is a verified development milestone, not evidence that the
whole Korean patch is complete.
# Manual Proof Routes

This groups the current screen-proof candidates by likely manual capture context, so the next verification pass can avoid one task per offset.

## Summary

- Screen-proof candidates: **7**
- Manual route groups: **3**
- Groups: **Kajiya, Tatsuji, Heishichi**

## Routes

### Route 1: Kajiya

- Candidate offsets: `0x0440C`
- Planned byte sets: `0xB5 0x93 0xAB`
- Screen hint: look for a blacksmith/shop or blacksmith-stage label
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`

| ROM | confidence | source bytes | planned bytes |
| --- | --- | ---: | --- |
| `0x0440C` | medium | 3 | `0xB5 0x93 0xAB` |

### Route 2: Tatsuji

- Candidate offsets: `0x048F4, 0x052A5, 0x05BE5`
- Planned byte sets: `0x89 0x98 0xA1`
- Screen hint: look for a visible Tatsuji boss/name context
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`

| ROM | confidence | source bytes | planned bytes |
| --- | --- | ---: | --- |
| `0x048F4` | medium | 3 | `0x89 0x98 0xA1` |
| `0x052A5` | medium | 3 | `0x89 0x98 0xA1` |
| `0x05BE5` | medium | 3 | `0x89 0x98 0xA1` |

### Route 3: Heishichi

- Candidate offsets: `0x06294, 0x0631B, 0x06359`
- Planned byte sets: `0x8D 0x8E 0x8F 0x90`
- Screen hint: look for a visible Heishichi name/dialogue context
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`

| ROM | confidence | source bytes | planned bytes |
| --- | --- | ---: | --- |
| `0x06294` | high | 4 | `0x8D 0x8E 0x8F 0x90` |
| `0x0631B` | high | 4 | `0x8D 0x8E 0x8F 0x90` |
| `0x06359` | high | 4 | `0x8D 0x8E 0x8F 0x90` |

## Rule

- Capture on the base Japanese ROM for these broad-scan proof routes.
- One route may produce evidence for more than one offset, but each promoted row still needs its own CPU-read match.
- If a route only shows the title/opening screen or no target text, stop and switch route instead of extending autoplay.

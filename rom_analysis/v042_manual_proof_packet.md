# v0.4.2 Manual Proof Packet

Use this instead of extending blind FCEUX autoplay when the emulator keeps repeating the first screen.

- Source: `rom_analysis\v042_text_promotion_readiness.json`
- Tasks: **7**
- Non-overlapping candidates: **4**
- Conflict alternatives: **3**
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua at the target screen: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Machine-readable result: `rom_analysis/manual_screen_dump_broad_scan/summary.json`

## Workflow

1. Open the base ROM in FCEUX.
2. Manually reach the related item/status/dialogue screen; do not keep extending autoplay on a stagnant title/start screen.
3. Pause on the screen with text visible.
4. Run `lua/kunio_manual_broad_scan_dump.lua` from the FCEUX Lua menu.
5. Run `python scripts/analyze_broad_scan_manual_dump.py` from the repository root.
6. Review `rom_analysis/manual_screen_dump_broad_scan/summary.json` and the screenshot/visible screen together.
7. Promote only rows with both a CPU read hit and matching visible screen context.

## Tasks

| # | kind | confidence | ROM | source | korean | original | planned v0.4.2 bytes | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | non_overlapping_needs_manual_screen | medium | `0x0440C` | かじや | 대장간 | `CA D0 E9` | `B5 93 AB` | read hit + screen context |
| 2 | non_overlapping_needs_manual_screen | medium | `0x048F4` | たつじ | 타츠지 | `07 09 03` | `89 98 A1` | read hit + screen context |
| 3 | non_overlapping_needs_manual_screen | medium | `0x052A5` | たつじ | 타츠지 | `82 84 7E` | `89 98 A1` | read hit + screen context |
| 4 | non_overlapping_needs_manual_screen | medium | `0x05BE5` | たつじ | 타츠지 | `97 99 93` | `89 98 A1` | read hit + screen context |
| 5 | conflict_alternative_needs_manual_screen | high | `0x06294` | へいしち | 헤이시치 | `9D 82 8C 91` | `8D 8E 8F 90` | read hit + screen context |
| 6 | conflict_alternative_needs_manual_screen | high | `0x0631B` | へいしち | 헤이시치 | `9D 82 8C 91` | `8D 8E 8F 90` | read hit + screen context |
| 7 | conflict_alternative_needs_manual_screen | high | `0x06359` | へいしち | 헤이시치 | `9D 82 8C 91` | `8D 8E 8F 90` | read hit + screen context |

## Notes

- The four non-overlapping rows are the safest first proof targets.
- The three conflict alternatives overlap earlier v0.4 interpretations and must decide between competing meanings.
- YouTube footage can help identify scene order and wording, but it cannot replace byte/read evidence for patch promotion.

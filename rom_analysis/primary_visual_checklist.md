# Primary Visual Checklist

This is the short visual-review queue for text rows already changed by the primary IPS.

## Summary

- Rows to visually verify: **10**
- Open patched ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Run watcher once: `lua/kunio_manual_v042_capture_watch.lua`
- Press `D` only on a screen that visibly matches one of the rows below.

| status | count |
| --- | ---: |
| `not_in_manual_capture_cards` | 10 |

## Priority Rows

| priority | ROM | romaji | source | Korean | evidence | capture status | screen hint |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | `0x07227` | Katana | かたな | 카타나 | `runtime-confirmed` | `not_in_manual_capture_cards` | look for a katana/weapon item label |
| 20 | `0x0569D` | Hashi | はし | 다리 | `encoding-exact` | `not_in_manual_capture_cards` | look for a bridge/stage/location label |
| 30 | `0x0561A` | Hashi | はし | 다리 | `static-candidate+pointer` | `not_in_manual_capture_cards` | look for a bridge/stage/location label |
| 30 | `0x05643` | Heishichi | へいしち | 헤이시치 | `static-candidate+pointer` | `not_in_manual_capture_cards` | look for a visible Heishichi name/dialogue context |
| 30 | `0x057D4` | Hashi | はし | 다리 | `static-candidate+pointer` | `not_in_manual_capture_cards` | look for a bridge/stage/location label |
| 30 | `0x0736A` | Raifu | ライフ | 라이프 | `static-candidate+pointer` | `not_in_manual_capture_cards` | look for a life/status UI label |
| 30 | `0x0739D` | Raifu | ライフ | 라이프 | `static-candidate+pointer` | `not_in_manual_capture_cards` | look for a life/status UI label |
| 40 | `0x0562F` | Tatsuichi | たついち | 타츠이치 | `static-candidate` | `not_in_manual_capture_cards` | look for a visible Tatsuichi name/dialogue context |
| 40 | `0x056DA` | Hashi | はし | 다리 | `static-candidate` | `not_in_manual_capture_cards` | look for a bridge/stage/location label |
| 40 | `0x0571C` | Hashi | はし | 다리 | `static-candidate` | `not_in_manual_capture_cards` | look for a bridge/stage/location label |

## Commands

```text
lua/kunio_manual_v042_capture_watch.lua
```

```powershell
python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v042 --output rom_analysis/manual_screen_dump_v042/summary.md
python scripts/generate_manual_capture_status.py
python scripts/generate_primary_visual_checklist.py
```

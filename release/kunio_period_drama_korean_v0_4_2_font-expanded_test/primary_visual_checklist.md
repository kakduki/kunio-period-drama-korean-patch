# Primary Visual Checklist

This is the short visual-review queue for text rows already changed by the primary IPS.

## Summary

- Rows to visually verify: **10**
- Visual confirmations: **0**
- Pending visual checks: **10**
- Auto-input byte-match rows: **10**
- Open patched ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Run watcher once: `lua/kunio_manual_v042_capture_watch.lua`
- Press `D` only on a screen that visibly matches one of the rows below.

| status | count |
| --- | ---: |
| `auto_input_match_needs_visual` | 10 |

## Priority Rows

| priority | ROM | romaji | human hint | source | Korean | evidence | auto matches | review status | screen hint |
| ---: | --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| 10 | `0x07227` | Katana | weapon/item label | かたな | 카타나 | `runtime-confirmed` | 1 | `auto_input_match_needs_visual` | look for a katana/weapon item label |
| 20 | `0x0569D` | Hashi | stage/location label | はし | 다리 | `encoding-exact` | 1 | `auto_input_match_needs_visual` | look for a bridge/stage/location label |
| 30 | `0x0561A` | Hashi | stage/location label | はし | 다리 | `static-candidate+pointer` | 1 | `auto_input_match_needs_visual` | look for a bridge/stage/location label |
| 30 | `0x05643` | Heishichi | name/dialogue label | へいしち | 헤이시치 | `static-candidate+pointer` | 1 | `auto_input_match_needs_visual` | look for a visible Heishichi name/dialogue context |
| 30 | `0x057D4` | Hashi | stage/location label | はし | 다리 | `static-candidate+pointer` | 1 | `auto_input_match_needs_visual` | look for a bridge/stage/location label |
| 30 | `0x0736A` | Raifu | UI life label | ライフ | 라이프 | `static-candidate+pointer` | 1 | `auto_input_match_needs_visual` | look for a life/status UI label |
| 30 | `0x0739D` | Raifu | UI life label | ライフ | 라이프 | `static-candidate+pointer` | 1 | `auto_input_match_needs_visual` | look for a life/status UI label |
| 40 | `0x0562F` | Tatsuichi | name/dialogue label | たついち | 타츠이치 | `static-candidate` | 1 | `auto_input_match_needs_visual` | look for a visible Tatsuichi name/dialogue context |
| 40 | `0x056DA` | Hashi | stage/location label | はし | 다리 | `static-candidate` | 1 | `auto_input_match_needs_visual` | look for a bridge/stage/location label |
| 40 | `0x0571C` | Hashi | stage/location label | はし | 다리 | `static-candidate` | 1 | `auto_input_match_needs_visual` | look for a bridge/stage/location label |

## Commands

```text
lua/kunio_manual_v042_capture_watch.lua
```

```powershell
python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v042 --output rom_analysis/manual_screen_dump_v042/summary.md
python scripts/record_primary_visual_review.py 0x07227 --confirm --screen-context "katana/weapon item label visible"
python scripts/generate_manual_capture_status.py
python scripts/generate_primary_visual_checklist.py
```

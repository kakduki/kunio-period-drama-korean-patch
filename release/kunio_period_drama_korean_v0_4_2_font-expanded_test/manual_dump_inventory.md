# Manual Dump Inventory

This inventory shows whether the manual FCEUX dump folders contain record files, screenshots, and summaries.

## Summary

- Dump dirs: **5**
- Total target-record files: **0**
- Total screenshot files: **0**
- Active matches in latest records: **0**

| folder | status | record files | screenshots | latest active matches | latest records | latest screenshot | summary |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `base` | `no_dump_records` | 0 | 0 | 0 | `-` | `-` | `-` |
| `v04` | `no_dump_records` | 0 | 0 | 0 | `-` | `-` | `-` |
| `v041` | `no_dump_records` | 0 | 0 | 0 | `-` | `-` | `-` |
| `v042` | `no_dump_records` | 0 | 0 | 0 | `-` | `-` | `-` |
| `broad_scan` | `no_dump_records` | 0 | 0 | 0 | `-` | `-` | `rom_analysis/manual_screen_dump_broad_scan/summary.md` |

## Rule

- `.gd` screenshots are kept as visual evidence from FCEUX `gui.gdscreenshot()`.
- A target-record byte match is not enough for promotion; confirm the visible screen context with `record_visual_review.py`.
- If all folders show `no_dump_records`, do not extend autoplay. Use `reference_capture_plan.md` to pick a concrete screen.

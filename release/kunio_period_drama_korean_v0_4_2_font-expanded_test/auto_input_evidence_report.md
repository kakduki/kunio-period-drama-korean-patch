# Auto-Input Evidence Report

This report ties the v0.4.2 scripted FCEUX route to its review image and active byte matches.

## Summary

- Frame: **883**
- Targets checked: **10**
- Active expected matches: **10**
- Matched primary rows: **10**
- Latest screenshot: `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen.gd`
- PNG review image: `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen.png`
- Review crops: `rom_analysis/fceux_input_explorer_v042/review_crops.json`
- Latest-frame crops: **2**
- Metadata: `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_meta.txt`
- Route note: Converted PNG confirms the auto-input route reached an in-game dialogue screen; this is not yet final patched-Korean visual approval.
- Current limit: This proves the scripted route reached an in-game dialogue screen and loaded the expected patched byte sequences into CPU memory. It does not by itself prove the final Korean glyphs are visually correct.

## Matched Rows

| ROM | romaji | hint | CPU range | expected bytes | review status |
| --- | --- | --- | --- | --- | --- |
| `0x0561A` | Hashi | look for a bridge/stage/location label | `$95BE-$960F` | `8B 8C` | `auto_input_match_needs_visual` |
| `0x0562F` | Tatsuichi | look for a visible Tatsuichi name/dialogue context | `$961A-$9623` | `89 98 8E 90` | `auto_input_match_needs_visual` |
| `0x05643` | Heishichi | look for a visible Heishichi name/dialogue context | `$9633-$9637` | `8D 8E 8F 90` | `auto_input_match_needs_visual` |
| `0x0569D` | Hashi | look for a bridge/stage/location label | `$968C-$968F` | `8B 8C` | `auto_input_match_needs_visual` |
| `0x056DA` | Hashi | look for a bridge/stage/location label | `$96C5-$96CE` | `8B 8C` | `auto_input_match_needs_visual` |
| `0x0571C` | Hashi | look for a bridge/stage/location label | `$9706-$9714` | `8B 8C` | `auto_input_match_needs_visual` |
| `0x057D4` | Hashi | look for a bridge/stage/location label | `$97C4-$97C8` | `8B 8C` | `auto_input_match_needs_visual` |
| `0x07227` | Katana | find a weapon/item list that visibly contains the Katana item; do not repeat the autoplay-route capture | `$B216-$B21A` | `88 89 8A` | `blocked_wrong_context_needs_inventory` |
| `0x0736A` | Raifu | look for a life/status UI label | `$B359-$B35E` | `96 8E 97` | `auto_input_match_needs_visual` |
| `0x0739D` | Raifu | look for a life/status UI label | `$B38C-$B391` | `96 8E 97` | `auto_input_match_needs_visual` |

## Latest-Frame Crops

| crop | image | region |
| --- | --- | --- |
| `dialogue_box` | `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen_dialogue_box.png` | 0,184 256x56 |
| `top_overlay` | `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen_top_overlay.png` | 0,0 256x24 |

## Interpretation

- Use this as route and byte-load evidence for the current automated path.
- Keep final visual approval separate until a patched-ROM screen visibly shows the intended Korean text in context.

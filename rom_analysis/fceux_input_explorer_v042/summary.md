# Manual Screen Dump Summary

- Input records: `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_target_records.tsv`
- Frame: **883**
- Targets checked: **10**
- Active expected matches: **10**
- Screenshot: `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_screen.gd`

## Active Matches

| label | category | ROM hit | CPU range | expected bytes | record snapshot |
| --- | --- | --- | --- | --- | --- |
| `v04_watch_rom_0561a_스테이지_7c` | 스테이지 | `ROM+0x0561A` | `$95BE-$960F` | `8B 8C` | `7B 15 96 15 96 15 96 15 96 15 96 15 96 15 96 15 96 15 96 15 96 05 7B 0A 7B 0F 7B 14 7B 29 96 2E 96 33 96 19 7B 3D 96 1E 7B 47 96 4C 96 51 96 23 7B 5B 96 60 96 65 96 28 7B 6F 96 2D 7B 79 96 7D 96 82 96 87 96 8C 96 91 96 96 96 9B 8B 8C 96 9F 8B FF` |
| `v04_watch_rom_0562f_보스_80` | 보스 | `ROM+0x0562F` | `$961A-$9623` | `89 98 8E 90` | `0C B6 83 87 91 89 98 8E 90 FF` |
| `v04_watch_rom_05643_보스_80` | 보스 | `ROM+0x05643` | `$9633-$9637` | `8D 8E 8F 90` | `8D 8E 8F 90 FF` |
| `v04_watch_rom_0569d_스테이지_7a` | 스테이지 | `ROM+0x0569D` | `$968C-$968F` | `8B 8C` | `85 8B 8C FF` |
| `v04_watch_rom_056da_스테이지_80` | 스테이지 | `ROM+0x056DA` | `$96C5-$96CE` | `8B 8C` | `9A 07 99 8D 89 8B 8C 0F 83 FF` |
| `v04_watch_rom_0571c_스테이지_78` | 스테이지 | `ROM+0x0571C` | `$9706-$9714` | `8B 8C` | `8E 87 0A AB 83 A6 8B 8C A3 AE 94 A3 9F 92 FF` |
| `v04_watch_rom_057d4_스테이지_8c` | 스테이지 | `ROM+0x057D4` | `$97C4-$97C8` | `8B 8C` | `8B 8C 8D 89 FF` |
| `v04_rom_07227_candidate_84` | 무기 | `ROM+0x07227` | `$B216-$B21A` | `88 89 8A` | `85 88 89 8A 00` |
| `v04_rom_0736a_candidate_93` | UI | `ROM+0x0736A` | `$B359-$B35E` | `96 8E 97` | `F0 96 8E 97 CB 00` |
| `v04_rom_0739d_candidate_93` | UI | `ROM+0x0739D` | `$B38C-$B391` | `96 8E 97` | `F0 96 8E 97 CA 00` |

## Captured Files

| file | bytes | kind |
| --- | ---: | --- |
| `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_cpu_ram.bin` | 2048 | `bin` |
| `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_cpu_ram.txt` | 7040 | `txt` |
| `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_meta.txt` | 168 | `txt` |
| `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_screen.gd` | 245771 | `gd` |
| `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_sram_6000_7fff.bin` | 8192 | `bin` |
| `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_sram_6000_7fff.txt` | 28160 | `txt` |
| `rom_analysis\fceux_input_explorer_v042\manual_frame_000883_target_records.tsv` | 1371 | `tsv` |

## Interpretation

- A match here means the manually reached screen has the expected candidate bytes mapped in CPU memory at the generated watch range.
- A non-match is still useful: it tells us this screen is not covered by the current Bank 1 target list and needs broader static matching or a new breakpoint target.
- The `.gd` screenshot is FCEUX/GD image data from `gui.gdscreenshot()`; keep it as evidence even if it is not directly viewable in every image viewer.

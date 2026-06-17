# FCEUX Padding Experiment PPU Watch Comparison

This compares same-frame, consecutive-VRAM PPU writes for the five `ROM+0x071A4` padding experiment ROMs.

Important: this is stricter than the phase-stream analyzer and avoids false positives caused by padding bytes such as `00` and `7A`.

| strategy | expected bytes | PPU writes | frames | final frame | exact VRAM matches | first locations | screen verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| pad_00 | `87 00 00` | 32160 | 148 | 3600 | 0 | - | not-visual-confirmed |
| pad_7a | `87 7A 7A` | 32160 | 148 | 3600 | 0 | - | not-visual-confirmed |
| pad_ff | `87 FF FF` | 32096 | 147 | 3600 | 0 | - | not-visual-confirmed |
| pad_f8f9 | `87 F8 F9` | 31982 | 121 | 3600 | 0 | - | not-visual-confirmed |
| preserve_tail | `87 88 AA` | 32160 | 148 | 3600 | 0 | - | not-visual-confirmed |

## Notes

- `not-visual-confirmed` means the bytes were checked in PPU writes, but no screenshot/PPU Viewer visual verdict has been made.
- The current autoplay Lua reaches the menu/status transfer window, but it is not yet a reliable full gameplay bot.
- Prefer strategies with exact VRAM matches for follow-up visual inspection.

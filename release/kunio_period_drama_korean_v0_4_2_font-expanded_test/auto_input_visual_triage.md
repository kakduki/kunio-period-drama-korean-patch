# Auto-Input Visual Triage

This separates byte-load evidence from final visual approval for the current scripted route.

## Decision

- Current auto-route scene: `opening_dialogue`
- Latest dialogue crop: `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen_dialogue_box.png`
- Byte-matched primary rows: **10**
- Visual approvals from this capture: **0**
- Next visual target: `0x07227` / Katana
- Next visual hint: look for a katana/weapon item label
- Decision: Do not mark any primary row visually confirmed from this auto-input capture. Use it as route/byte-load evidence and adjust the next route toward the target context.

## Row Triage

| ROM | romaji | byte match | visual confirmed | reason |
| --- | --- | --- | --- | --- |
| `0x0561A` | Hashi | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x0562F` | Tatsuichi | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x05643` | Heishichi | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x0569D` | Hashi | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x056DA` | Hashi | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x0571C` | Hashi | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x057D4` | Hashi | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x07227` | Katana | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x0736A` | Raifu | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |
| `0x0739D` | Raifu | true | false | current auto-input capture is opening dialogue evidence, not the target visual context |

## Next Step

- Keep the auto-input route evidence, but route the emulator to the `Katana` item/weapon label before recording visual approval.

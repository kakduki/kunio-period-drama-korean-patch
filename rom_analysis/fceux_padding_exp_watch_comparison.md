# FCEUX Padding Experiment Watch Comparison

This compares CPU read-watch results for the five `ROM+0x071A4` padding experiment ROMs.

Important: this validates that each strategy's bytes become active in the watched CPU record. It does not validate visible rendering.

| strategy | expected bytes | hits | active expected matches | final frame | final reason | record snapshot | screen verdict |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| pad_00 | `87 00 00` | 11 | 11 | 3600 | lua_done | `9F B4 87 00 00 A6 83 CA F8 F9 00` | not-checked |
| pad_7a | `87 7A 7A` | 11 | 11 | 3600 | lua_done | `9F B4 87 7A 7A A6 83 CA F8 F9 00` | not-checked |
| pad_ff | `87 FF FF` | 4 | 4 | 3600 | lua_done | `9F B4 87 FF FF A6 83 CA F8 F9 00` | not-checked |
| pad_f8f9 | `87 F8 F9` | 9 | 9 | 3600 | lua_done | `9F B4 87 F8 F9 A6 83 CA F8 F9 00` | not-checked |
| preserve_tail | `87 88 AA` | 11 | 11 | 3600 | lua_done | `9F B4 87 88 AA A6 83 CA F8 F9 00` | not-checked |

## Notes

- All strategies need a separate visual/PPU check before any padding rule is promoted.
- Differing hit counts can happen when a padding byte changes control flow or terminator behavior; treat this as a signal to inspect the status screen carefully.
- `preserve_tail` is only a baseline because it keeps old tail bytes after the new first glyph.

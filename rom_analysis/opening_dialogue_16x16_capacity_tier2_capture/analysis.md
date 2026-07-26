# Opening Dialogue Proof Smoke Test

Overall smoke result: **PASS**
Overall proof result: **PASS**

| check | result |
| --- | --- |
| bounded_lua_completion | PASS |
| screen_capture | PASS |
| nametable_capture | PASS |
| target_record_runtime_read | PASS |
| visual_korean_glyph_review | PASS |

- Final Lua reason: `lua_done`
- Registered target read hits: `37`
- Matched target read hits: `37`
- Visual note: Native frame 883 review: all 17 paired 16x16 syllables, including runtime-only C0-C7 source slots, are distinct with no visible opening-scene background or UI damage. Forced omission of normal spacing and speaker separator keeps this a capacity probe, not release text.

The visual verdict is recorded separately from boot/runtime evidence.

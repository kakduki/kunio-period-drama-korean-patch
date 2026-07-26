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
- Registered target read hits: `45`
- Matched target read hits: `45`
- Visual note: Native frame 883 review: the expanded paired 16x16 text reads as '쿠니마사 어서 움직여!' and '분조 두목이 큰일이야!' with distinct syllables and preserved spaces. No visible opening-scene background or UI damage. Pointer 183 preservation is statically verified, but its own runtime context is not captured here.

The visual verdict is recorded separately from boot/runtime evidence.

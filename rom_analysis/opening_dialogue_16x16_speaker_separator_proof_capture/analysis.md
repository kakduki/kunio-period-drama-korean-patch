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
- Registered target read hits: `47`
- Matched target read hits: `47`
- Visual note: Native frame 883 review: the local paired 16x16 colon clearly separates the speaker name in '쿠니마사: 어서 움직여!' while both Korean lines remain readable with preserved spaces. No visible opening-scene background or UI damage. The raw 0xBB byte is intentionally absent from this Korean record, so this is a visible speaker-separator surrogate proof rather than a universal control-byte decoder.

The visual verdict is recorded separately from boot/runtime evidence.

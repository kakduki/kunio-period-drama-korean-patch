# Opening Dialogue Renderer Probe

Status: **ROUTINE_TRACE_CAPTURED**

| check | result |
| --- | --- |
| bounded_lua_completion | PASS |
| screen_capture | PASS |
| target_parser_execution | PASS |
| target_source_reads | PASS |
| target_emit_prep_execution | PASS |
| target_emit_dispatch_execution | PASS |
| renderer_buffer_writes | UNKNOWN |
| renderer_queue_writes | PASS |
| unrelated_oam_activity | OBSERVED |
| dialogue_nametable_writes | PASS |
| ppu_rows_captured | PASS |

- Final Lua reason: `lua_done`
- Parser hits by label: `{'emit_dispatch': 34, 'emit_prep': 34, 'parser': 37}`
- Parser source bytes: `{'00': 6, '06': 3, '0F': 3, '13': 3, '1C': 6, '82': 3, '83': 3, '84': 3, '85': 3, '86': 3, '88': 6, '8B': 3, '8C': 3, '93': 3, '95': 3, '96': 3, '98': 3, '9A': 3, '9D': 3, '9F': 3, 'A4': 6, 'AE': 12, 'B2': 6, 'BB': 3, 'CA': 6, 'F8': 1, 'F9': 1, 'FF': 1}`
- Parser PCs: `{'915A': 37, '955F': 34, '9593': 34}`
- Source-read PCs: `{'915A': 37}`
- Target source reads: `37`
- Renderer-buffer writes: `0`
- Renderer-queue writes: `424`
- Unrelated OAM tile-code writes: `1366`
- Unrelated OAM DMA writes: `823`
- Dialogue-nametable writes: `456`

The OAM activity above belongs to gameplay sprites, not this dialogue path.
The relevant evidence is the source-read, queue, and nametable path. The
8x16 candidate must still pass a bounded native-screen readability review.

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
| target_emitted_tile_rows | PASS |
| unrelated_oam_activity | OBSERVED |
| dialogue_nametable_writes | PASS |
| ppu_rows_captured | PASS |

- Final Lua reason: `lua_done`
- Parser hits by label: `{'emit_dispatch': 17, 'emit_prep': 17, 'parser': 18}`
- Parser source bytes: `{'00': 6, '81': 3, '82': 3, '83': 3, '84': 3, '85': 3, '86': 3, '87': 3, '88': 3, '89': 3, '8A': 3, '8B': 3, '8C': 3, 'C8': 3, 'C9': 3, 'CA': 3, 'FF': 1}`
- Parser PCs: `{'915A': 18, '955F': 17, '9593': 17}`
- Source-read PCs: `{'915A': 18}`
- Target source reads: `18`
- Renderer-buffer writes: `0`
- Renderer-queue writes: `288`
- Target emitted tile rows: `34`
- Unrelated OAM tile-code writes: `1366`
- Unrelated OAM DMA writes: `823`
- Dialogue-nametable writes: `456`

The OAM activity above belongs to gameplay sprites, not this dialogue path.
The relevant evidence is the source-read, queue, and nametable path. The
8x16 candidate must still pass a bounded native-screen readability review.

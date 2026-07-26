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
- Parser hits by label: `{'emit_dispatch': 45, 'emit_prep': 45, 'parser': 47}`
- Parser source bytes: `{'00': 15, '81': 3, '82': 3, '83': 3, '84': 3, '85': 3, '86': 3, '87': 3, '88': 3, '89': 3, '8A': 3, '8B': 3, '8C': 3, '8D': 3, '8E': 3, '8F': 3, '90': 3, '91': 3, '92': 3, '93': 3, '94': 3, '95': 3, '96': 3, '97': 3, '98': 3, '99': 3, '9A': 3, 'C0': 3, 'C1': 3, 'C2': 3, 'C3': 3, 'C4': 6, 'C5': 6, 'C6': 3, 'C7': 3, 'C8': 3, 'C9': 3, 'CA': 6, 'F8': 1, 'FF': 1}`
- Parser PCs: `{'915A': 47, '955F': 45, '9593': 45}`
- Source-read PCs: `{'915A': 37}`
- Target source reads: `37`
- Renderer-buffer writes: `0`
- Renderer-queue writes: `512`
- Target emitted tile rows: `90`
- Unrelated OAM tile-code writes: `1366`
- Unrelated OAM DMA writes: `823`
- Dialogue-nametable writes: `456`

The OAM activity above belongs to gameplay sprites, not this dialogue path.
The relevant evidence is the source-read, queue, and nametable path. The
8x16 candidate must still pass a bounded native-screen readability review.

# Late Pointer Runtime Follow-up (2026-08-06)

## Scope

This probe used the verified Japanese base ROM and the original pointer-table
addresses for p196-p201. It used the bounded renderer-context trace with an
800-frame observation window after the first source read. No candidate bytes
were promoted or patched from this run.

## Result

| pointer | first read | complete record match | PPU writes in observation window | lower dialogue band writes | classification |
|---|---:|---:|---:|---:|---|
| p196 | none | none | none | none | `UNKNOWN_NOT_REACHED` |
| p197 | 5384 | no | 277 | 0 | `UNKNOWN_PARTIAL_SOURCE_READ_NON_DIALOGUE_BAND` |
| p198 | none | none | none | none | `UNKNOWN_NOT_REACHED` |
| p199 | none | none | none | none | `UNKNOWN_NOT_REACHED` |
| p200 | none | none | none | none | `UNKNOWN_NOT_REACHED` |
| p201 | none | none | none | none | `UNKNOWN_NOT_REACHED` |

For p197, the observed PPU writes covered `$2023-$22E6`, not the lower
conversation band beginning at `$2302`. The target never reached a complete
13-byte source-record match. The writes therefore do not prove that p197 is a
visible dialogue record in this route, and they are not safe native-patch
promotion evidence.

## Reproduction

```powershell
python scripts/generate_manifest_runtime_target.py --candidate "rom\\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --pointer-index 196 --pointer-index 197 --pointer-index 198 --pointer-index 199 --pointer-index 200 --pointer-index 201 --output C:\tmp\kunio_base_ptr196_201_targets_2026_08_06.lua
python scripts/run_fceux_lua_analysis.py --rom "rom\\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\\kunio_full_pointer_batch_196_201_trace.lua --target-lua C:\tmp\kunio_base_ptr196_201_targets_2026_08_06.lua --frames 8000 --timeout 120 --final-output C:\tmp\kunio_base_ptr196_201_runtime_window800_2026_08_06 --clean-output --no-dump-hex --no-dump-bin --no-stagnation-abort --lua-env KUNIO_RENDER_WINDOW=800
```

The launcher timed out externally after the bounded run budget; the Lua output
contains the complete `first_read` and `window_done` records shown above. This
is a route limitation, not a native patch failure.

## Gate Decision

- p196-p201 promotion: `FAIL_NOT_PROVEN` (no rows promoted)
- natural enemy-clear/boss transition: `UNKNOWN`
- release status: `NOT_READY`
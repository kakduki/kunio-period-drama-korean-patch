# Native Visual Comparison

Date: 2026-08-05

This is a bounded comparison between the Japanese base ROM and the eight-row
manifest candidate. Both runs used the same opening-route Lua trace. The
renderer trace confirmed that the dialogue transfer writes to nametable
`$2302` onward, which is the lower dialogue band (screen y approximately
192..224). The earlier report checked y=112..144 and therefore under-reported
rows after p182.

## Inputs

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Candidate ROM: `C:/tmp/kunio_manifest_p182_p189_rebuild.nes`
- Fixed visual trace: `lua/kunio_manifest_native_visual_trace.lua`
- Renderer trace: `lua/kunio_manifest_renderer_context_trace.lua`
- Base target pointers: PRG offsets `0x071B6..0x0727F`
- Candidate target pointers: PRG offsets `0x05FC4..0x06052`

## Results

| Row | Candidate PPU writes | Base PPU writes | PPU byte differences | Changed pixels y=160..240 | Soft gate |
|---:|---:|---:|---:|---:|---|
| p182 | 48 | 68 | 27 | 656 | PASS |
| p183 | 26 | 40 | 13 | 355 | PASS |
| p184 | 24 | 42 | 12 | 366 | PASS |
| p185 | 20 | 28 | 9 | 227 | PASS |
| p186 | 36 | 80 | 19 | 707 | PASS |
| p187 | 26 | 12 | 6 | 208 | PASS |
| p188 | 40 | 54 | 23 | 590 | PASS |
| p189 | 40 | 48 | 20 | 526 | PASS |

Every row reached a complete source-record read, wrote candidate-specific
bytes to the dialogue nametable band, and produced a nonzero lower-band pixel
difference against the Japanese base capture. This is sufficient for the
soft native visual gate for rows p182-p189. It does not prove unrelated menu,
combat, boss, save/load, or ending contexts.

## Artifacts

- Candidate renderer trace: `C:/tmp/kunio_manifest_p182_p189_renderer_context_v5/`
- Base renderer trace: `C:/tmp/kunio_manifest_base_p182_p189_renderer_context_v5/`
- Candidate fixed captures: `C:/tmp/kunio_manifest_p182_p189_native_visual_delayed/`
- Base fixed captures: `C:/tmp/kunio_manifest_base_p182_p189_native_visual/`

The eight-row manifest is now promoted from candidate-only to the main
translation manifest. The overall release build remains `NOT_READY` until the
broader release gates are completed.
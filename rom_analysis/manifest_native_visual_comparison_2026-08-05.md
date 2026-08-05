# Native Visual Comparison

Date: 2026-08-05

This is a bounded comparison between the Japanese base ROM and the eight-row
manifest candidate. Both runs used the same opening-route Lua trace. The
window trace captured frames at 0, 16, 32, 48, 64, 80, 96, 112, 128, 144,
and 160 frames after a complete target-span read.

## Inputs

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Candidate ROM: `C:/tmp/kunio_manifest_p182_p189_rebuild.nes`
- Fixed trace: `lua/kunio_manifest_native_visual_trace.lua`
- Window trace: `lua/kunio_manifest_native_visual_window.lua`
- Base target pointers: PRG offsets `0x071B6..0x0727F`
- Candidate target pointers: PRG offsets `0x05FC4..0x06052`

## Results

| Row | Complete-read capture | Dialogue-band change in 0..160 frames | Soft gate |
|---:|---:|---:|---|
| p182 | 26 reads; all window samples differ | 534..1104 changed pixels | PASS |
| p183 | 14 reads | 0 pixels | UNKNOWN |
| p184 | 13 reads | 0..10 pixels only; no string-shaped change | UNKNOWN |
| p185 | 11 reads | 0..2 pixels only; no string-shaped change | UNKNOWN |
| p186 | 20 reads | 0 pixels | UNKNOWN |
| p187 | 14 reads | 0 pixels | UNKNOWN |
| p188 | 22 reads | 0..10 pixels only; no string-shaped change | UNKNOWN |
| p189 | 22 reads | 0 pixels | UNKNOWN |

The complete-read condition prevents the earlier initial-buffer false positive.
The p182 result is consistent with a real rendered-string change. For
p183-p189, the target bytes are read and the loader progression is observed,
but the candidate/base pixel comparison does not show a corresponding
string-shaped change in the dialogue band, even after 160 frames. These rows
remain candidate-only; they must not be promoted without a corrected pointer,
renderer-context trace, or manual visual evidence.

## Artifacts

- Candidate fixed captures: `C:/tmp/kunio_manifest_p182_p189_native_visual_delayed/`
- Base fixed captures: `C:/tmp/kunio_manifest_base_p182_p189_native_visual/`
- Candidate window captures: `C:/tmp/kunio_manifest_p182_p189_native_window_v4/`
- Base window captures: `C:/tmp/kunio_manifest_base_p182_p189_native_window_v4/`
- Converted spot checks: `rom_analysis/native_visual_base_p182.png`,
  `rom_analysis/native_visual_p182.png`, `rom_analysis/native_visual_base_p186.png`,
  `rom_analysis/native_visual_p186.png`

This report does not change the release gate. The release build remains
`NOT_READY`.
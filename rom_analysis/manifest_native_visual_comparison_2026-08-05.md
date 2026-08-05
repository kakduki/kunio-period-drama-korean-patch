# Native Visual Comparison

Date: 2026-08-05

This is a bounded comparison between the Japanese base ROM and the eight-row
manifest candidate. Both runs used the same opening-route Lua trace and
captured a screenshot 30 frames after the target string was read.

## Inputs

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Candidate ROM: `C:/tmp/kunio_manifest_p182_p189_rebuild.nes`
- Trace: `lua/kunio_manifest_native_visual_trace.lua`
- Base target pointers: PRG offsets `0x071B6..0x0727F`
- Candidate target pointers: PRG offsets `0x05FC4..0x06052`

## Results

| Row | Base frame | Candidate frame | Pixel-diff result | Soft gate |
|---:|---:|---:|---|---|
| p182 | 746 | 724 | 1,799 changed pixels; differences concentrate in dialogue rows y=112..144 | PASS |
| p183 | 1107 | 1071 | not compared in this bounded pass | UNKNOWN |
| p184 | 1413 | 1357 | not compared in this bounded pass | UNKNOWN |
| p185 | 1703 | 1639 | not compared in this bounded pass | UNKNOWN |
| p186 | 2047 | 1937 | 763 changed pixels; no corresponding dialogue-row change detected | UNKNOWN |
| p187 | 2321 | 2225 | not compared in this bounded pass | UNKNOWN |
| p188 | 2639 | 2527 | not compared in this bounded pass | UNKNOWN |
| p189 | 2999 | 2879 | not compared in this bounded pass | UNKNOWN |

The p182 result is consistent with a real rendered-string change. The p186
result is not sufficient to claim that the Korean string was rendered; the
observed changes are outside the expected dialogue text band. Rows p186-p189
remain candidate-only until their own dialogue-region comparison or manual
visual evidence passes.

## Artifacts

- Candidate captures: `C:/tmp/kunio_manifest_p182_p189_native_visual_delayed/`
- Base captures: `C:/tmp/kunio_manifest_base_p182_p189_native_visual/`
- Converted spot checks: `rom_analysis/native_visual_base_p182.png`,
  `rom_analysis/native_visual_p182.png`, `rom_analysis/native_visual_base_p186.png`,
  `rom_analysis/native_visual_p186.png`

This report does not change the release gate. The release build remains
`NOT_READY`.

# Minimum Feature Proof Recheck

Date: 2026-08-05
Status: `PASS_MINIMUM_FEATURE_SOFT_GATE`
Release status: `NOT_READY`

## Base and Reference

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Base size: `262160` bytes
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Reference IPS: `tools/reference/TSe-v10.ips`
- Reference IPS is used only for structural ownership and renderer/font mapping.

## One Verified Display String

- Korean text: `쿠니마사: 어서 움직여! 분조 두목이 큰일이야!`
- Context: opening dialogue screen
- Pointer index: `182`
- Pointer table ROM offset: `0x05F40`
- Record ROM offset: `0x071B6`
- PRG bank: `1` (CPU window `$8000-$BFFF`)
- Runtime CPU range: `$B1A6-$B1D4`
- Record length: `47` bytes, original length `37`
- Rendering: paired 8x16 cells forming 16x16 Korean glyphs; local paired colon replaces the renderer-special speaker separator.
- Neighbor safety: pointer `183` is relocated from `0x071DB` to `0x07FF6` / CPU `$BFE6`.

## Reproducible Candidate Build

```powershell
python scripts/build_opening_dialogue_16x16_capacity.py `
  "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" `
  --reference-ips tools\reference\TSe-v10.ips `
  --catalog text_data\korean_scene_batches\opening_ptr_182_16x16_speaker_separator_proof.json `
  --out-dir "$env:TEMP\speaker_build" `
  --out-stem kunio_speaker `
  --report-json "$env:TEMP\speaker_build.json" `
  --report-markdown "$env:TEMP\speaker_build.md"
```

Recheck output:

- Candidate size: `262160` bytes
- Candidate MD5: `3384157d7e72f3bf4dd3f742ffe41fc9`
- Changed-byte spans: `94`
- Escaped bytes outside declared ranges: `0`
- Generated IPS MD5: `A9DF164AC05EE36FF05CCE0B1E5952A2`
- Generated IPS SHA-256: `4E515D46926140197BA9EB20A5FCB2D91B7C967AD620114759348C93DA427E6A`

## Bounded FCEUX Proof

- Lua route: `lua/kunio_opening_dialogue_proof.lua`
- Target definition: `lua/kunio_opening_dialogue_16x16_speaker_separator_proof_target.lua`
- Frame ceiling: `920`
- Capture frame: `883`
- Completion: `lua_done`
- Registered reads: `47`
- Matched reads: `47`
- Full record target match: `true`
- Screen capture: `PASS`
- Nametable capture: `PASS`
- Native visual review: `PASS`, using the checked-in frame-883 speaker-separator review for the identical candidate MD5.

Runtime output was regenerated outside the repository at:
`%TEMP%\speaker_build_legacy_recheck_runtime_full`.

This proves the first actual Korean screen string and its ROM/PRG-bank/context mapping. It does not prove all dialogue, natural boss progression, shared CHR safety across every screen, or release readiness.
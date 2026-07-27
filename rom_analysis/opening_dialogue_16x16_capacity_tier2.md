# Opening Dialogue Paired 16x16 Capacity Candidate

Status: **SOFT_GATE_PASS_OPENING_CAPACITY_RUNTIME_AND_VISUAL**

This bounded candidate reads all code-pair and helper-range decisions from
its scene catalog. The runtime probe now proves the named opening record and
its captured screen context; it does not promote its compact wording or the
additional source codes to a release-wide font contract.

## Scope

- Batch: `opening_ptr_182_16x16_capacity_tier2`
- Pointer index: `182`
- Record ROM offset: `0x071B6`
- Candidate wording: 쿠니마사어서움직여! / 분조두목큰일이야
- Unique glyphs: `17`; source slots: `34`.
- Helper range: `0x81-0xC7`.
- English-reference source slots: `26`.
- Runtime-proven additional source slots: `0xC0-0xC7` (8 codes), giving this
  opening route `34` observed source slots in total.

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `6785f321c0fad8d08f4c929aba7c865d`
- Changed-byte spans: `86`; escaped bytes: `0`.
- IPS: `output\opening_dialogue_16x16_capacity_tier2\kunio_period_drama_korean_opening_dialogue_16x16_capacity_tier2.ips`
- ROM: `output\opening_dialogue_16x16_capacity_tier2\kunio_period_drama_korean_opening_dialogue_16x16_capacity_tier2.nes`

## Runtime Evidence

- Bounded FCEUX route: frame `883`, terminal reason `lua_done`.
- Target source record: CPU `$B1A6`, ROM `0x071B6`; `37/37` source reads
  matched the catalog bytes, including `C0 C1 C2 C3 C4 C5 C6 C7`.
- Emitted tile pairs: `C0/E0`, `C1/E1`, `C2/E2`, `C3/E3`, `C4/E4`,
  `C5/E5`, `C6/E6`, `C7/E7`; mapper state remained `R0=3C, R1=3E`.
- Native screenshot: `rom_analysis/opening_dialogue_16x16_capacity_tier2_capture/renderer_probe_frame_000883_screen.png`.
- Detailed logs: `source_reads.tsv`, `emitted_tiles.tsv`, and
  `renderer_probe_summary.tsv` in the same capture directory.

This is a development soft-gate PASS for the opening capacity proof. Release
promotion still requires a non-opening route, lifecycle-safe page strategy,
and per-context evidence.

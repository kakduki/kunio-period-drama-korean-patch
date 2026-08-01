# Pre-Pointer High-Code Runtime Evidence

- Candidate MD5: `50617961a99d43be949cc28e2ff092a5`.
- English reference MD5: `63e1d902807981f524af97748cd99500`.
- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Owner contract: PRG Bank 1, CPU `$8000 + (ROM offset - $4010)`, high input codes `$81-$9A`, CHR Bank 7 top tile base `$181`, bottom delta `$20`.

## Bounded Probe

| run | exact CPU owner matches | completed | capture | PPU read | status |
| --- | ---: | --- | ---: | --- | --- |
| English reference | 10/10 | `lua_done` at frame 900 | 285 | PASS | `PASS_CPU_OWNER_PPU_CAPTURE` |
| Korean composed candidate | 10/10 | `lua_done` at frame 900 | 285 | PASS | `PASS_CPU_OWNER_PPU_CAPTURE_VISUAL_UNKNOWN` |

The Korean run observed all ten exact Bank 1 CPU owners, including `EN-PRE-138`, during this bounded route.

## Main Menu Context

Both English and Korean runs reached the bounded capture at frame 1906 with `lua_done` and successful PPU nametable reads. The English run recorded 7,766 extra source reads in the watched Bank 1 window; the Korean candidate recorded 7,280. The native GD screenshots are retained locally but are not sufficient for pixel-level approval.

## Gate

- Static candidate build and English-structure composition: PASS.
- Exact source-owner probe: PASS for 10/10 Korean rows.
- PPU capture availability: PASS.
- Per-row visual attribution, shared-page safety, and natural boss progression: UNKNOWN.
- Release status: `NOT_READY`.

Machine-readable details are in `rom_analysis/pre_pointer_high_runtime.json`.

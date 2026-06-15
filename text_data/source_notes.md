# Text source notes

## YouTube gameplay reference

- URL: `https://www.youtube.com/watch?v=W9OHjavh6Lw&t=15s`
- Role: supplemental dialogue/menu transcription source.

The video can help confirm visible Japanese dialogue, menu flow, and scene
order. It does not replace ROM/FCEUX analysis for patching, because the patch
still needs the in-ROM text location, tile/code mapping, control bytes, and
space constraints.

Recommended workflow:

1. Use the video to transcribe visible Japanese lines and scene order.
2. Store transcription and Korean draft translations under `text_data/`.
3. Use FCEUX Lua traces in `rom_analysis/` to connect visible lines to runtime
   nametable writes and, eventually, PRG text/source data.

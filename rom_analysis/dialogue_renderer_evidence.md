# Dialogue Renderer Evidence

This is a static code-path record, not a decoded dialogue script.

## Verified

- Parser ROM offset: 0x08256
- Parser PRG bank: 2
- Primary input stream: zero-page 0x05
- Secondary input stream: zero-page 0x07
- Low-nibble branch: mask 0x0F, threshold 0x0E
- Explicit special bytes: 0x8A, 0x8B, 0xAC, 0xB0, 0xBB, 0xFA
- Per-mode mask lookup: CPU 0x829E, ROM 0x082AE
- Mask values: 0x00, 0x03, 0x01, 0x01

## Consequence

A Bank 1 dialogue byte is processed with a second stream and control branches.
Do not treat it as a universal direct tile index or decode it with the menu-only glyph hypothesis.
The Japanese columns in script_catalog.tsv must remain tokenized until one known
dialogue record has a traced source byte to emitted-tile proof.

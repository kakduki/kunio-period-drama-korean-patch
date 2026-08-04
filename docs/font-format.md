# Font Format

The NES screen renders tile indices, not Unicode characters. Korean support therefore has two independent parts:

1. a code-to-tile character map;
2. CHR tile graphics that contain the Korean glyphs.

The existing `font/char_map.json`, generated tile binaries, and `scripts/korean_tile_font.py` are the current implementation reference. A font change must identify its CHR file offset, bank/page, tile count, and the character-map entries it owns.

## Verification

- Every inserted character must have a tile mapping.
- The generated CHR must preserve unrelated tiles and the expected NES tile format.
- Runtime byte reads and a native emulator screenshot are separate checks. Passing the first does not imply that the second passed.

The project currently has an opening-screen Korean visual proof and several bounded runtime proofs, but not a full-game visual proof.

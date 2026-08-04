# Korean Font Strategy

The first milestone is one Korean word or label rendered on a real game screen. The project uses a compact tile font and a controlled character map rather than attempting to cover all Hangul syllables at once.

## Staged coverage

1. Prove the existing fixed labels and one opening dialogue string.
2. Add the small set of Hangul syllables required by the next confirmed scene.
3. Rebuild the CHR tail and update only the verified character map entries.
4. Expand coverage from the translation manifest, measuring width before insertion.

## Layout rules

- Prefer short natural Korean phrasing that fits the original line and page limits.
- Do not use a missing glyph as a substitute for an unreviewed character.
- Keep punctuation and control codes explicit in the manifest.
- Mark a string `MISSING_GLYPH` until the font builder produces the required tile and the runtime path reads it.

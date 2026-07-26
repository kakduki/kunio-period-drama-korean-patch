# Opening Dialogue 16x16 Korean Proof Candidate

Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_FONT_16X16**

This proof does not invent a new dialogue queue. Each Korean syllable is
a pair of adjacent, existing 8x16 dialogue cells, forming one native 16x16
glyph. The underlying 8x16 target-record gate has already been captured;
this candidate still needs its own bounded native-screen review.

## Scope

- Pointer index: `182`
- Record ROM offset: `0x071B6`
- Proof wording: 쿠니마사: 어서! 분조!
- Unique proof glyphs: `8`; source slots: `16`.
- This compact wording is a font proof only, not the final release translation.

## Bounds

- Renderer entry hook: `0x0556F` -> `0x955F`
- Renderer marker hook: `0x05586` -> `0x9576`
- Same-page code cave: `0x07FB5` -> `0xBFA5`
- The hook executes only for record `$B1A6` and safe source codes `0x81-0x93`.
- The English reference validates source-slot structure only; no English pixels or text are copied.

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `3d33831dbf424ad673ece9f9bf6d0701`
- Changed-byte spans: `41`; escaped bytes: `0`.
- IPS: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\opening_dialogue_16x16_proof\kunio_period_drama_korean_opening_dialogue_16x16_proof.ips`
- ROM: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\opening_dialogue_16x16_proof\kunio_period_drama_korean_opening_dialogue_16x16_proof.nes`

The only runtime check is the known opening route, capped at one capture
frame. It stops immediately after the capture rather than entering gameplay.

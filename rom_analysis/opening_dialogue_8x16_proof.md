# Opening Dialogue 8x16 Korean Proof Candidate

Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_FONT_8X16**

This is a one-record renderer proof, not a release patch. It keeps the
original pointer and record length, then uses the renderer's existing two
vertical tile writes to display one Korean glyph as an 8x16 pair.

## Source

- Pointer index: `182`
- Pointer ROM offset: `0x05F40` (unchanged)
- Record ROM offset: `0x071B6`
- Korean proof: 쿠니마사: 어서 움직여! 분조 두목이 큰일이야!

## Bounded Renderer Change

- Renderer entry hook: `0x0556F` -> `0x955F`
- Renderer marker hook: `0x05586` -> `0x9576`
- Same-page code cave: `0x07FB5` -> `0xBFA5`
- Only record `$B1A6` and source codes `0x81-0x93` enter the 8x16 path.
- All other renderer inputs replay the original control flow.

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `22ca16ea7bfe8eede57e2f7bd3f98ef4`
- Changed-byte spans: `18`; escaped bytes: `0`.
- IPS: `output\opening_dialogue_8x16_proof\kunio_period_drama_korean_opening_dialogue_8x16_proof.ips`
- ROM: `output\opening_dialogue_8x16_proof\kunio_period_drama_korean_opening_dialogue_8x16_proof.nes`

The candidate must pass the bounded opening capture and a native-size
readability review before it can replace the 8x8 baseline.

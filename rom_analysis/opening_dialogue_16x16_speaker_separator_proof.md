# Opening Dialogue Paired 16x16 Capacity Candidate

Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_CAPACITY**

This bounded candidate reads all code-pair and helper-range decisions from
its scene catalog. Passing it proves only the named opening record and the
captured screen context; it does not promote its compact wording to release text.

## Scope

- Batch: `opening_ptr_182_16x16_speaker_separator_proof`
- Pointer index: `182`
- Record ROM offset: `0x071B6`
- Record bytes: `47` (base: `37`).
- Candidate wording: 쿠니마사: 어서 움직여! 분조 두목이 큰일이야!
- Unique glyphs: `18`; source slots: `36`.
- Helper range: `0x81-0xC9`.
- English-reference source slots: `26`.
- Preserved neighbour pointer: `183` at `0x05F42`.
- Preserved neighbour record: `0x071DB` -> `0x07FF6` / `0xBFE6`.

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `3384157d7e72f3bf4dd3f742ffe41fc9`
- Changed-byte spans: `94`; escaped bytes: `0`.
- IPS: `output\opening_dialogue_16x16_speaker_separator_proof\kunio_period_drama_korean_opening_dialogue_16x16_speaker_separator_proof.ips`
- ROM: `output\opening_dialogue_16x16_speaker_separator_proof\kunio_period_drama_korean_opening_dialogue_16x16_speaker_separator_proof.nes`

Promotion requires the same bounded frame-883 capture, exact runtime
record bytes, and a native screenshot with no visible background/UI damage.

# Opening Dialogue Paired 16x16 Capacity Candidate

Status: **PROOF_CANDIDATE_VISUALLY_VERIFIED**

This bounded candidate reads all code-pair and helper-range decisions from
its scene catalog. Passing it proves only the named opening record and the
captured screen context; it does not promote its compact wording to release text.

## Scope

- Batch: `opening_ptr_182_16x16_readability_proof`
- Pointer index: `182`
- Record ROM offset: `0x071B6`
- Record bytes: `38` (base: `37`).
- Candidate wording: 쿠니오: 서둘러! 분조 두목이 위험해!
- Unique glyphs: `15`; source slots: `30`.
- Helper range: `0x81-0xC9`.
- English-reference source slots: `26`.
- Preserved neighbour pointer: `183` at `0x05F42`.
- Preserved neighbour record: `0x071DB` -> `0x07FF6` / `0xBFE6`.

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `bf6a8d5b88eea45ea37fc15080603d29`
- Changed-byte spans: `106`; escaped bytes: `0`.
- IPS: `output\opening_dialogue_16x16_readability_proof\kunio_period_drama_korean_opening_dialogue_16x16_readability_proof.ips`
- ROM: `output\opening_dialogue_16x16_readability_proof\kunio_period_drama_korean_opening_dialogue_16x16_readability_proof.nes`

Promotion requires the same bounded frame-883 capture, exact runtime
record bytes, and a native screenshot with no visible background/UI damage.

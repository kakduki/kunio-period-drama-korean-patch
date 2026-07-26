# Opening Korean 16x16 Candidate

Status: **CANDIDATE_BUILT_NOT_RUNTIME_VERIFIED**

This candidate packs only the opening records declared by its catalog.
It is a font-capacity and record-boundary candidate, not a release
translation batch.

## Scope

- Glyphs: `20` / source slots: `40`.
- Source ranges: 0x81-0x9F, 0xC0-0xC8.
- Helper: `88` bytes; marker hook `0xBFDD`.
- Guard: `record_base_range` (`0xB1A6-0xB1E0`).
- Pointer 182: `0x071B6` / `0xB1A6` (32 bytes): 쿠니오: 서둘러! 분조두목 위험!
- Pointer 183: `0x071D6` / `0xB1C6` (25 bytes): 오코토: 쿠니오! 기다렸어!
- Pointer 184: `0x071EF` / `0xB1DF` (23 bytes): 쿠니오: 오코토, 오랜만.

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `46cedd1da6d49643f5dd6bc4895ce706`
- Changed spans: `129`; escaped bytes: `0`.
- IPS: `output/opening_ptr_182_184_16x16_readability/kunio_period_drama_korean_opening_ptr_182_184_16x16_readability.ips`
- ROM: `output/opening_ptr_182_184_16x16_readability/kunio_period_drama_korean_opening_ptr_182_184_16x16_readability.nes`

Promotion requires bounded capture, matching runtime reads, and native
readability review for every declared opening record.

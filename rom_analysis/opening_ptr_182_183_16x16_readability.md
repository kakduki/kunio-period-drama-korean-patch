# Two-Record Opening Korean 16x16 Candidate

Status: **CANDIDATE_BUILT_NOT_RUNTIME_VERIFIED**

This candidate packs two context-confirmed opening records without using
unbounded gameplay. It is a font-capacity and record-boundary candidate,
not a release translation batch.

## Scope

- Glyphs: `19` / source slots: `38`.
- Source ranges: 0x81-0x9E, 0xC0-0xC7.
- Helper: `88` bytes; marker hook `0xBFDD`.
- Pointer 182: `0x071B6` / `0xB1A6` (33 bytes): 쿠니오: 서둘러! 분조두목 위험!
- Pointer 183: `0x071D7` / `0xB1C7` (25 bytes): 오코토: 쿠니오! 기다렸어!

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `d1bd6e285c818ed60890282d8704f80a`
- Changed spans: `126`; escaped bytes: `0`.
- IPS: `output/opening_ptr_182_183_16x16_readability/kunio_period_drama_korean_opening_ptr_182_183_16x16_readability.ips`
- ROM: `output/opening_ptr_182_183_16x16_readability/kunio_period_drama_korean_opening_ptr_182_183_16x16_readability.nes`

Promotion requires the separate bounded pointer-182 and pointer-183
captures, matching runtime reads, and native readability review for both screens.

# Reference-Guided Capture Plan

This plan uses the text transcription/reference to choose which screens are worth reaching manually.
It does not treat YouTube or transcription order as ROM proof.

## Summary

- Queue rows: **60**
- Focused rows: **20**
- Focused rows that are length-safe promotion candidates: **7**
- Focused rows font-ready after v0.4.2: **19**

## Focused Capture Plan

| rank | score | section | ROM | expected text | Korean | CPU guess | proof status | v0.4.2 bytes | screen hint |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1380 | 6. 적 캐릭터 / 보스 이름 | `0x06294` | へいしち | 헤이시치 | `$A284` | `needs_manual_capture` | `0x8D 0x8E 0x8F 0x90` | look for a visible Heishichi name/dialogue context |
| 2 | 1380 | 6. 적 캐릭터 / 보스 이름 | `0x0631B` | へいしち | 헤이시치 | `$A30B` | `needs_manual_capture` | `0x8D 0x8E 0x8F 0x90` | look for a visible Heishichi name/dialogue context |
| 3 | 1380 | 6. 적 캐릭터 / 보스 이름 | `0x06359` | へいしち | 헤이시치 | `$A349` | `needs_manual_capture` | `0x8D 0x8E 0x8F 0x90` | look for a visible Heishichi name/dialogue context |
| 4 | 1320 | 6. 적 캐릭터 / 보스 이름 | `0x048F4` | たつじ | 타츠지 | `$88E4` | `needs_manual_capture` | `0x89 0x98 0xA1` | look for a visible Tatsuji boss/name context |
| 5 | 1320 | 6. 적 캐릭터 / 보스 이름 | `0x052A5` | たつじ | 타츠지 | `$9295` | `needs_manual_capture` | `0x89 0x98 0xA1` | look for a visible Tatsuji boss/name context |
| 6 | 1320 | 6. 적 캐릭터 / 보스 이름 | `0x05BE5` | たつじ | 타츠지 | `$9BD5` | `needs_manual_capture` | `0x89 0x98 0xA1` | look for a visible Tatsuji boss/name context |
| 7 | 1280 | 7. 스테이지 / 지역 이름 | `0x0440C` | かじや | 대장간 | `$83FC` | `needs_manual_capture` | `0xB5 0x93 0xAB` | look for a blacksmith/shop or blacksmith-stage label |
| 8 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x17D61` | ちから | 힘 | `$BD51` | `not_in_v043_proof_packet` | `0x87` | look for a strength/status stat label |
| 9 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x17D69` | ちから | 힘 | `$BD59` | `not_in_v043_proof_packet` | `0x87` | look for a strength/status stat label |
| 10 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x17D81` | ちから | 힘 | `$BD71` | `not_in_v043_proof_packet` | `0x87` | look for a strength/status stat label |
| 11 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x095B9` | おかね | 돈 | `$95A9` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 12 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x0966F` | おかね | 돈 | `$965F` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 13 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x09830` | おかね | 돈 | `$9820` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 14 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x0EE3D` | おかね | 돈 | `$AE2D` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 15 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x0F3D1` | おかね | 돈 | `$B3C1` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 16 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x10D75` | おかね | 돈 | `$8D65` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 17 | 1060 | 3. 스테이터스 / UI 텍스트 | `0x10FD5` | おかね | 돈 | `$8FC5` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 18 | 1000 | 3. 스테이터스 / UI 텍스트 | `0x1CA00` | おかね | 돈 | `$89F0` | `not_in_v043_proof_packet` | `0x95` | look for the UI text screen (돈/소지금) |
| 19 | 960 | 4. 아이템 / 무기 이름 | `0x1BB7E` | くすり | 약 | `$BB6E` | `not_in_v043_proof_packet` | `0x92` | look for the 회복 text screen (약 (기본 회복)) |
| 20 | 940 | 3. 스테이터스 / UI 텍스트 | `0x02D68` | うごき | 움직임 | `$AD58` | `not_in_v043_proof_packet` | `-` | look for the 능력치 text screen (움직임/속도 (능력치)) |

## Rule

- This file is a navigation aid for FCEUX/manual video review.
- A row becomes patchable only after `v043_proof_status.md` shows CPU-read proof and visual confirmation.
- Stop any autoplay route that stays on the title/first screen; use this plan to pick a concrete screen instead.

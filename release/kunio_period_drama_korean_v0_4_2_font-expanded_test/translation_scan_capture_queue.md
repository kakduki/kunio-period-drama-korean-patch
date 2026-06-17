# Translation Scan Capture Queue

Manual verification queue generated from `translation_pattern_scan`.
These are not approved patch offsets until a real screen dump confirms them.

## Summary

- Scan new hits: **113**
- Queued hits: **60**
- High confidence: **6**
- Medium confidence: **33**
- Low confidence: **21**

## Queue

| priority | confidence | human hint | expected text | Korean | romaji | group | ROM | bank | CPU guess | screen hint | reason |
| ---: | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 10 | high | name/dialogue label | へいしち | 헤이시치 | Heishichi | event/dialogue | `0x06294` | 1 | `$A284` | look for a visible Heishichi name/dialogue context | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | name/dialogue label | へいしち | 헤이시치 | Heishichi | event/dialogue | `0x06359` | 1 | `$A349` | look for a visible Heishichi name/dialogue context | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | name/dialogue label | へいしち | 헤이시치 | Heishichi | event/dialogue | `0x0631B` | 1 | `$A30B` | look for a visible Heishichi name/dialogue context | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | 이벤트 | 賭場でお金稼ぎ | 도박장에서 돈벌이 | TOBA de okane kasegi | event/dialogue | `0x06499` | 1 | `$A489` | look for the 이벤트 text screen (도박장에서 돈벌이) | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | 이벤트 | 賭場でお金稼ぎ | 도박장에서 돈벌이 | TOBA de okane kasegi | event/dialogue | `0x07450` | 1 | `$B440` | look for the 이벤트 text screen (도박장에서 돈벌이) | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | 스테이지 | はかば | 묘지 | Hakaba | other | `0x0560E` | 1 | `$95FE` | look for the 스테이지 text screen (묘지) | strong Bank 1 text-like hit; capture the related screen |
| 15 | medium | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x052A5` | 1 | `$9295` | look for a visible Tatsuji boss/name context | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | 스테이지 | はやし | 숲 | Hayashi | other | `0x0637B` | 1 | `$A36B` | look for the 스테이지 text screen (숲) | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | blacksmith/stage label | かじや | 대장간 | Kajiya | other | `0x0440C` | 1 | `$83FC` | look for a blacksmith/shop or blacksmith-stage label | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | 무기 | チェーン | 체인 | Cheen | items/equipment | `0x07587` | 1 | `$B577` | look for the 무기 text screen (체인) | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | 이벤트 | 賭場でお金稼ぎ | 도박장에서 돈벌이 | TOBA de okane kasegi | event/dialogue | `0x0589C` | 1 | `$988C` | look for the 이벤트 text screen (도박장에서 돈벌이) | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x05BE5` | 1 | `$9BD5` | look for a visible Tatsuji boss/name context | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | 스테이지 | とざん | 등산 | Tozan | other | `0x060BD` | 1 | `$A0AD` | look for the 스테이지 text screen (등산) | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | 대사 | まけた… | 졌다… | Maketa... | other | `0x04242` | 1 | `$8232` | look for the 대사 text screen (패배 시) | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x048F4` | 1 | `$88E4` | look for a visible Tatsuji boss/name context | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | 스테이지 | はかば | 묘지 | Hakaba | other | `0x05F67` | 1 | `$9F57` | look for the 스테이지 text screen (묘지) | Bank 1 text-like hit with uncommon shift; capture before patching |
| 25 | medium | UI | おかね | 돈 | Okane | ui/status | `0x0F3D1` | 3 | `$B3C1` | look for the UI text screen (돈/소지금) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | おかね | 돈 | Okane | ui/status | `0x095B9` | 2 | `$95A9` | look for the UI text screen (돈/소지금) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | status stat label | ちから | 힘 | Chikara | ui/status | `0x17D61` | 5 | `$BD51` | look for a strength/status stat label | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | status stat label | ちから | 힘 | Chikara | ui/status | `0x17D69` | 5 | `$BD59` | look for a strength/status stat label | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | status stat label | ちから | 힘 | Chikara | ui/status | `0x17D81` | 5 | `$BD71` | look for a strength/status stat label | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x1CB80` | 7 | `$8B70` | look for a visible Tatsuji boss/name context | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | おかね | 돈 | Okane | ui/status | `0x0EE3D` | 3 | `$AE2D` | look for the UI text screen (돈/소지금) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | 엔딩 | おわり | 끝 | Owari | event/dialogue | `0x10921` | 4 | `$8911` | look for the 엔딩 text screen (끝) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | たべる | 먹다 | Taberu | ui/status | `0x11332` | 4 | `$9322` | look for the UI text screen (먹다 (아이템 사용)) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | 능력치 | うごき | 움직임 | Ugoki | ui/status | `0x17D18` | 5 | `$BD08` | look for the 능력치 text screen (움직임/속도 (능력치)) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | 엔딩 | おわり | 끝 | Owari | event/dialogue | `0x02999` | 0 | `$A989` | look for the 엔딩 text screen (끝) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | おかね | 돈 | Okane | ui/status | `0x09830` | 2 | `$9820` | look for the UI text screen (돈/소지금) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | すてる | 버리다 | Suteru | ui/status | `0x0CEAD` | 3 | `$8E9D` | look for the UI text screen (버리다 (아이템 폐기)) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | レベル | 레벨 | Reberu | ui/status | `0x1281B` | 4 | `$A80B` | look for the UI text screen (Level) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | 엔딩 | おわり | 끝 | Owari | event/dialogue | `0x1F0B1` | 7 | `$B0A1` | look for the 엔딩 text screen (끝) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | たべる | 먹다 | Taberu | ui/status | `0x1FA3C` | 7 | `$BA2C` | look for the UI text screen (먹다 (아이템 사용)) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | 능력치 | うごき | 움직임 | Ugoki | ui/status | `0x02D68` | 0 | `$AD58` | look for the 능력치 text screen (움직임/속도 (능력치)) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | おかね | 돈 | Okane | ui/status | `0x0966F` | 2 | `$965F` | look for the UI text screen (돈/소지금) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x10561` | 4 | `$8551` | look for a visible Tatsuji boss/name context | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | おかね | 돈 | Okane | ui/status | `0x10D75` | 4 | `$8D65` | look for the UI text screen (돈/소지금) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | おかね | 돈 | Okane | ui/status | `0x10FD5` | 4 | `$8FC5` | look for the UI text screen (돈/소지금) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | UI | たべる | 먹다 | Taberu | ui/status | `0x11340` | 4 | `$9330` | look for the UI text screen (먹다 (아이템 사용)) | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x1ADBD` | 6 | `$ADAD` | look for a visible Tatsuji boss/name context | non-Bank 1 text-like hit; useful for later bank expansion |
| 60 | low | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x131F0` | 4 | `$B1E0` | look for a visible Tatsuji boss/name context | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 대사 | まけた… | 졌다… | Maketa... | other | `0x0A255` | 2 | `$A245` | look for the 대사 text screen (패배 시) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | はたけ | 밭 | Hatake | other | `0x12F21` | 4 | `$AF11` | look for the 스테이지 text screen (밭) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x1317F` | 4 | `$B16F` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x1319D` | 4 | `$B18D` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x1318D` | 4 | `$B17D` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 회복 | くすり | 약 | Kusuri | other | `0x1BB7E` | 6 | `$BB6E` | look for the 회복 text screen (약 (기본 회복)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | はかば | 묘지 | Hakaba | other | `0x0D080` | 3 | `$9070` | look for the 스테이지 text screen (묘지) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x16F72` | 5 | `$AF62` | look for a visible Tatsuji boss/name context | broad scan hit; defer unless the exact screen is reached |
| 60 | low | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x131D8` | 4 | `$B1C8` | look for a visible Tatsuji boss/name context | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x10E68` | 4 | `$8E58` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x0D339` | 3 | `$9329` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x0D588` | 3 | `$9578` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x0E9FA` | 3 | `$A9EA` | look for a visible Tatsuji boss/name context | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x0F0E2` | 3 | `$B0D2` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | はかば | 묘지 | Hakaba | other | `0x1019C` | 4 | `$818C` | look for the 스테이지 text screen (묘지) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | UI | おかね | 돈 | Okane | ui/status | `0x1CA00` | 7 | `$89F0` | look for the UI text screen (돈/소지금) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | はかば | 묘지 | Hakaba | other | `0x119E9` | 4 | `$99D9` | look for the 스테이지 text screen (묘지) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x18926` | 6 | `$8916` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | 스테이지 | じごく | 지옥 | Jigoku | other | `0x1A63B` | 6 | `$A62B` | look for the 스테이지 text screen (지옥 (스테이지)) | broad scan hit; defer unless the exact screen is reached |
| 60 | low | boss/name label | たつじ | 타츠지 | Tatsuji | event/dialogue | `0x1A6AC` | 6 | `$A69C` | look for a visible Tatsuji boss/name context | broad scan hit; defer unless the exact screen is reached |

## Notes

- CPU address is a best-effort 16KB bank-window guess for debugger watching.
- `expected text` and `Korean` are display labels joined from `translation_readable_reference.json` when possible.
- Low-confidence rows often contain control-like bytes and should not be patched from static evidence.
- This queue supplements `manual_capture_queue.md`; it does not replace the v0.4 verification queue.

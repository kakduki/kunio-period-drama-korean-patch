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

| priority | confidence | source | korean | group | ROM | bank | CPU guess | add | bytes | reason |
| ---: | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| 10 | high | へいしち | 헤이시치 | event/dialogue | `0x06294` | 1 | `$A284` | `0x80` | `9D 82 8C 91` | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | へいしち | 헤이시치 | event/dialogue | `0x06359` | 1 | `$A349` | `0x80` | `9D 82 8C 91` | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | へいしち | 헤이시치 | event/dialogue | `0x0631B` | 1 | `$A30B` | `0x80` | `9D 82 8C 91` | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | 賭場でお金稼ぎ | 도박장에서 돈벌이 | event/dialogue | `0x06499` | 1 | `$A489` | `0x80` | `93 85 87` | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | 賭場でお金稼ぎ | 도박장에서 돈벌이 | event/dialogue | `0x07450` | 1 | `$B440` | `0x80` | `93 85 87` | strong Bank 1 text-like hit; capture the related screen |
| 10 | high | はかば | 묘지 | other | `0x0560E` | 1 | `$95FE` | `0x7C` | `96 82 96` | strong Bank 1 text-like hit; capture the related screen |
| 15 | medium | たつじ | 타츠지 | event/dialogue | `0x052A5` | 1 | `$9295` | `0x72` | `82 84 7E` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | はやし | 숲 | other | `0x0637B` | 1 | `$A36B` | `0x89` | `A3 AE 95` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | かじや | 대장간 | other | `0x0440C` | 1 | `$83FC` | `0xC4` | `CA D0 E9` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | チェーン | 체인 | items/equipment | `0x07587` | 1 | `$B577` | `0x7F` | `90 83 AE` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | 賭場でお金稼ぎ | 도박장에서 돈벌이 | event/dialogue | `0x0589C` | 1 | `$988C` | `0x93` | `A6 98 9A` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | たつじ | 타츠지 | event/dialogue | `0x05BE5` | 1 | `$9BD5` | `0x87` | `97 99 93` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | とざん | 등산 | other | `0x060BD` | 1 | `$A0AD` | `0x77` | `8B 82 A6` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | まけた… | 졌다… | other | `0x04242` | 1 | `$8232` | `0x08` | `28 11 18` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | たつじ | 타츠지 | event/dialogue | `0x048F4` | 1 | `$88E4` | `0xF7` | `07 09 03` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 15 | medium | はかば | 묘지 | other | `0x05F67` | 1 | `$9F57` | `0x99` | `B3 9F B3` | Bank 1 text-like hit with uncommon shift; capture before patching |
| 25 | medium | おかね | 돈 | ui/status | `0x0F3D1` | 3 | `$B3C1` | `0xFF` | `04 05 17` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おかね | 돈 | ui/status | `0x095B9` | 2 | `$95A9` | `0xC2` | `C7 C8 DA` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | ちから | 힘 | ui/status | `0x17D61` | 5 | `$BD51` | `0x76` | `87 7C 9E` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | ちから | 힘 | ui/status | `0x17D69` | 5 | `$BD59` | `0x76` | `87 7C 9E` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | ちから | 힘 | ui/status | `0x17D81` | 5 | `$BD71` | `0x76` | `87 7C 9E` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | たつじ | 타츠지 | event/dialogue | `0x1CB80` | 7 | `$8B70` | `0x07` | `17 19 13` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おかね | 돈 | ui/status | `0x0EE3D` | 3 | `$AE2D` | `0x07` | `0C 0D 1F` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おわり | 끝 | event/dialogue | `0x10921` | 4 | `$8911` | `0x5C` | `61 89 85` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | たべる | 먹다 | ui/status | `0x11332` | 4 | `$9322` | `0xE6` | `F6 03 10` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | うごき | 움직임 | ui/status | `0x17D18` | 5 | `$BD08` | `0x75` | `78 7F 7C` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おわり | 끝 | event/dialogue | `0x02999` | 0 | `$A989` | `0xA4` | `A9 D1 CD` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おかね | 돈 | ui/status | `0x09830` | 2 | `$9820` | `0x71` | `76 77 89` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | すてる | 버리다 | ui/status | `0x0CEAD` | 3 | `$8E9D` | `0xFD` | `0A 10 27` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | レベル | 레벨 | ui/status | `0x1281B` | 4 | `$A80B` | `0xE4` | `0F 01 0E` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おわり | 끝 | event/dialogue | `0x1F0B1` | 7 | `$B0A1` | `0xC0` | `C5 ED E9` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | たべる | 먹다 | ui/status | `0x1FA3C` | 7 | `$BA2C` | `0xE6` | `F6 03 10` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | うごき | 움직임 | ui/status | `0x02D68` | 0 | `$AD58` | `0x4C` | `4F 56 53` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おかね | 돈 | ui/status | `0x0966F` | 2 | `$965F` | `0x71` | `76 77 89` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | たつじ | 타츠지 | event/dialogue | `0x10561` | 4 | `$8551` | `0x0A` | `1A 1C 16` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おかね | 돈 | ui/status | `0x10D75` | 4 | `$8D65` | `0xFF` | `04 05 17` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | おかね | 돈 | ui/status | `0x10FD5` | 4 | `$8FC5` | `0xFD` | `02 03 15` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | たべる | 먹다 | ui/status | `0x11340` | 4 | `$9330` | `0xE6` | `F6 03 10` | non-Bank 1 text-like hit; useful for later bank expansion |
| 25 | medium | たつじ | 타츠지 | event/dialogue | `0x1ADBD` | 6 | `$ADAD` | `0x0A` | `1A 1C 16` | non-Bank 1 text-like hit; useful for later bank expansion |
| 60 | low | たつじ | 타츠지 | event/dialogue | `0x131F0` | 4 | `$B1E0` | `0xF0` | `00 02 FC` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | まけた… | 졌다… | other | `0x0A255` | 2 | `$A245` | `0xD0` | `F0 D9 E0` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | はたけ | 밭 | other | `0x12F21` | 4 | `$AF11` | `0xF7` | `11 07 00` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x1317F` | 4 | `$B16F` | `0xF8` | `04 02 00` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x1319D` | 4 | `$B18D` | `0xF8` | `04 02 00` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x1318D` | 4 | `$B17D` | `0xF6` | `02 00 FE` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | くすり | 약 | other | `0x1BB7E` | 6 | `$BB6E` | `0xF8` | `00 05 21` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | はかば | 묘지 | other | `0x0D080` | 3 | `$9070` | `0x98` | `B2 9E B2` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | たつじ | 타츠지 | event/dialogue | `0x16F72` | 5 | `$AF62` | `0xF3` | `03 05 FF` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | たつじ | 타츠지 | event/dialogue | `0x131D8` | 4 | `$B1C8` | `0xF0` | `00 02 FC` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x10E68` | 4 | `$8E58` | `0xF8` | `04 02 00` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x0D339` | 3 | `$9329` | `0xFC` | `08 06 04` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x0D588` | 3 | `$9578` | `0xFF` | `0B 09 07` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | たつじ | 타츠지 | event/dialogue | `0x0E9FA` | 3 | `$A9EA` | `0xF4` | `04 06 00` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x0F0E2` | 3 | `$B0D2` | `0xF8` | `04 02 00` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | はかば | 묘지 | other | `0x1019C` | 4 | `$818C` | `0x7B` | `95 81 95` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | おかね | 돈 | ui/status | `0x1CA00` | 7 | `$89F0` | `0xFA` | `FF 00 12` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | はかば | 묘지 | other | `0x119E9` | 4 | `$99D9` | `0xEA` | `04 F0 04` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x18926` | 6 | `$8916` | `0xF8` | `04 02 00` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | じごく | 지옥 | other | `0x1A63B` | 6 | `$A62B` | `0xFD` | `09 07 05` | broad scan hit; defer unless the exact screen is reached |
| 60 | low | たつじ | 타츠지 | event/dialogue | `0x1A6AC` | 6 | `$A69C` | `0xF4` | `04 06 00` | broad scan hit; defer unless the exact screen is reached |

## Notes

- CPU address is a best-effort 16KB bank-window guess for debugger watching.
- Low-confidence rows often contain control-like bytes and should not be patched from static evidence.
- This queue supplements `manual_capture_queue.md`; it does not replace the v0.4 verification queue.

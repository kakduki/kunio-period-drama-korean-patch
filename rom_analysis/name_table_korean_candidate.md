# Name-Table Korean Candidate

Focused soft-gate proof candidate for the renderer family used by the effective name-table source table.

- Input candidate: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\full_nonpointer_korean_candidate\kunio_period_drama_korean_full_nonpointer_candidate.nes
- Candidate ROM: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\name_table_korean_candidate\kunio_period_drama_korean_name_table_candidate.nes
- Candidate IPS: C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\name_table_korean_candidate\kunio_period_drama_korean_name_table_candidate.ips
- Input MD5: 18284402f073b91c09d05f52a16b9b9d
- Candidate MD5: df586e888e23761d2da518162444810e
- Source ROM range: 0x3FB32
- Source bytes: 88 96 9F 8B -> 81 82 81 82
- Test text: 다리다리
- Expected PPU target: 0x2043-0x2046
- PPU sequence: 88 96 9F 8B -> 81 82 81 82
- Runtime contract: PPUCTRL 0x88, MMC3 R1 0x3E, physical CHR Bank 7, tile 0x100 + code.
- Source-owner probe result: physical ROM offset 0x3FB32; 0x0561B was not active on this route.

## Scope

- This candidate changes only one visible four-byte source record and four CHR glyph slots.
- The text is intentionally a bounded test string; it is not a release translation.
- PASS requires the PPU trace to show 81 82 81 82 at 0x2043-0x2046 and the screenshot to show the Korean glyphs.
- Runtime source and screenshot proof are recorded for one context; release status remains NOT_READY.

## Glyph Slots

| code | glyph | CHR ROM offset |
| --- | --- | --- |
| 0x81 | 다 | 0x2F820 |
| 0x82 | 리 | 0x2F830 |
| 0x81 | 다 | 0x2F840 |
| 0x82 | 리 | 0x2F850 |

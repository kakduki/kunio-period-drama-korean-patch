# Korean Development Candidate

Status: **CANDIDATE_BUILT_PENDING_COMBINED_RUNTIME_SMOKE**

## Components

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Opening candidate: `46cedd1da6d49643f5dd6bc4895ce706`.
- Menu clone source: **original Japanese base ROM**.
- Font quality: **PASS**.
- The menu clone is copied from the Japanese base before opening glyph changes are layered in.

## Candidate

- ROM: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\korean_development_candidate\kunio_period_drama_korean_development_candidate.nes`.
- IPS: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\korean_development_candidate\kunio_period_drama_korean_development_candidate.ips`.
- Candidate MD5: `6474e2d857dbbcbf1ce8f1e5d8201c08`.
- Opening changed bytes: `1325`.
- Menu changed bytes: `1970`.
- Total changed bytes: `3295`.

## Limits

- This combines three opening records and the main-menu label candidate only.
- The menu clone is based on the original CHR page so opening glyphs do not leak into Items.
- Other dialogue records, gameplay text, cursor lifecycle, and full Items Korean text remain unpromoted.

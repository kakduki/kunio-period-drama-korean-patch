# Opening 16x16 Korean Font Profile Comparison

These are literal one-bit NES tile pixels, not a high-resolution mockup.
The triage result narrows candidates; native FCEUX capture remains decisive.

| profile | target | threshold | resample | density | min distance | edge touches | triage |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| malgun-bold-baseline | 15 | 100 | lanczos | 0.3469 | 36 | 15 | REVIEW |
| malgun-bold-airy | 14 | 145 | box | 0.2719 | 28 | 0 | PASS |
| nanum-extra-bold | 14 | 135 | box | 0.2667 | 35 | 0 | PASS |
| kopub-dotum-bold | 14 | 135 | box | 0.2766 | 27 | 0 | PASS |
| gulim-screen | 14 | 135 | box | 0.1440 | 24 | 0 | REVIEW |

- Glyph set: `쿠니오서둘러분조두목이위험해:`
- Recommended prototype profile: `malgun-bold-airy`
- Preview: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\rom_analysis\opening_font_profile_comparison\profiles.png`

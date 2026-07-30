# Expanded CHR and 8x16 Decision

Status: **8X16_PROFILE_SELECTED_FOR_FULL_DIALOGUE_PIPELINE**

## Expanded CHR

- Base layout: 16 CHR banks, 262,160-byte ROM.
- Probe layout: 17 CHR banks, 270,352-byte ROM.
- PTR-181 mapped appended Bank 16 with `R1=86`.
- Existing 16 CHR banks remained byte-identical.
- Target frame 392 displayed Korean and preserved the field.
- The 7200-frame route restored `R1=3E` and matched the conditional candidate's
  46 checkpoint fingerprints.

Result: **PASS**. IPS generation and application now support ROM extension.

## Square 16x16 Expansion

The boundary probe displayed `한글확장코드검증`, including source codes
`8A/8B`, `9F`, `C0`, `C8`, `CB`, and `DF`. The text rendered, but changing
the broad `C0-FF` tile area removed the field background.

Result: **FAIL_FONT_PAGE_BACKGROUND_COLLISION**. A 28-syllable square page is
not promoted merely because its bytes and mapper address work.

## Narrow 8x16 Semantic Candidate

- Pointer: PTR-181 / CPU `$B188`.
- Korean draft: `츠우: 형님 / 기다려!`.
- One source code per Hangul syllable.
- Frame 392: Korean text identifiable, field preserved, `R1=86`.
- Frame 7200: finite `lua_done`, 46 unique screens, restored `R0/R1=3C/3E`.

Result: **PASS_DEVELOPMENT_READABILITY_AND_LIFECYCLE**.

The 8x16 profile doubles syllable capacity relative to paired 16x16. The
optimized 248-pointer draft now needs 49 pages, within the 64 appended MMC3
2KB-page budget. Translation wording and punctuation still require review
before release.

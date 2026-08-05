# Full Text Extraction Coverage (2026-08-06)

## Extraction Run

The verified Japanese base ROM was processed with
`python tools/extract_text.py`. The output was written outside the repository
at `C:/tmp/kunio_text_extract_2026_08_06` so raw ROM-derived files are not
added to the release repository.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Pointer table: `0x05DD4-0x05FC3`
- Extracted pointer rows: `248`
- Conservative catalog rows missing: `PTR-012`, `PTR-022`, `PTR-162`,
  `PTR-244`, `PTR-247`
- Structural rows with conservative ownership: `243`

## Korean Worklist Coverage

The regenerated catalog now reflects the current native development gate:

| status | rows |
| --- | ---: |
| development-verified opening (`PTR-182`-`PTR-195`) | 14 |
| structural unknown | 229 |
| structural unknown and missing conservative row | 5 |

The separate translation manifest contains 17 rows: 14 pointer-dialogue rows
and 3 menu/action rows. All 17 have non-empty development translations, but
only the 14 opening pointer rows are included in the current native dialogue
candidate. The remaining 234 pointer rows are deliberately not translated or
patched from English wording alone.

## Decision

`PASS_EXTRACTION_COVERAGE_RECORDED`

The extractor and catalog now agree on the full 248-row pointer worklist and
current 14-row native gate. This is not full-game translation completion:
Japanese meaning, renderer context, route evidence, font allocation, and
bounded visual proof are still missing for the unknown rows.
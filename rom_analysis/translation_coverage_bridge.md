# Translation Coverage Bridge

This report joins the readable Korean translation list to static ROM scan candidates.
It does not promote any candidate to a patch target: runtime proof is required.

## Inputs

- Translation reference: `text_data\translation_readable_reference.json`
- Pattern scan: `rom_analysis\translation_pattern_scan.json`
- Translation entries: **144**
- Entries with at least one static candidate: **24**

## Status Counts

| Status | Count |
| --- | ---: |
| `no_static_candidate` | 115 |
| `skipped_by_scanner` | 5 |
| `static_candidate_known_bank1` | 8 |
| `static_candidate_unverified` | 16 |

## Interpretation

- `static_candidate_known_bank1` means the scan intersects an existing Bank 1 candidate pool; it is not runtime proof.
- `static_candidate_unverified` means a byte-pattern hit exists outside the known Bank 1 target set.
- `no_static_candidate` means the current scanner found no safe byte-pattern candidate, not that the text is absent from the ROM.
- `skipped_by_scanner` means the scanner intentionally excluded the entry, usually because it has too few encodable kana.
- Every row remains `not_runtime_proven` until CPU read, screen/context, and candidate build evidence are recorded.

Detailed rows: `translation_coverage_bridge.csv` and `translation_coverage_bridge.json`.

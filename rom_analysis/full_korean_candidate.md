# Full Korean Candidate

Status: **COMPOSED_CANDIDATE_BUILT_RUNTIME_UNKNOWN**

## Composed Stages

1. Full pointer-dialogue compiler using the English pointer/control skeleton.
2. Bounded 16x16 Korean main-menu template and isolated source-page glyph slots.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `d062b19d23050cd4e148e22fbfff57b7`.
- Candidate ROM: `output\full_korean_candidate\kunio_period_drama_korean_full_candidate.nes`.
- Candidate IPS: `output\full_korean_candidate\kunio_period_drama_korean_full_candidate.ips`.
- Full pointer records: `247`; bytes: `3820`.
- Main-menu targets: `57`.
- Korean square-font gate: **PASS**.

## English Reference Coverage

- English changed bytes: `12582`.
- Korean bytes inside English record spans: `5371`.
- Fully covered records by same-offset audit: `3`.
- Partial records: `7`; missing records: `89`.
- Same-offset coverage is an ownership audit, not visual or translation proof.

## Limits

- This is not a final release ROM.
- Growth, name-table, status, item, technique, and other non-pointer renderers remain open.
- Boot, menu, dialogue, and interaction-route smoke tests are required before promotion.

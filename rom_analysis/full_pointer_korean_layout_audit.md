# Full Pointer Korean Layout Audit

Status: **PASS**

- Active records: `244`
- Maximum segment: `24` / `24` cells
- Hard failures: `0`
- Warnings over 20 cells: `1`

| pointer | page | segment cells | max | Korean draft |
| ---: | ---: | --- | ---: | --- |
| 153 | 14 | `24` | 24 | 우리는 이것과 저것을 가지고 있습니다 |

The count is conservative: retained punctuation and variable bytes count
as cells. This is a static development gate, not a substitute for release
screenshots.

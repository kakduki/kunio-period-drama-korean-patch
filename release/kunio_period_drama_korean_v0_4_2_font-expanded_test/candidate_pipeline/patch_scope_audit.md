# Patch Scope Audit

This audit compares each soft-gate candidate ROM against its font-expanded base ROM.
It catches accidental edits outside the planned PRG replacement spans.

- Rows: **15**
- Status counts: `{'PASS': 15, 'FAIL': 0, 'SKIP': 0}`
- All pass: `True`

| build id | status | changed offsets | expected offsets | spans | failure class |
| --- | --- | ---: | ---: | --- | --- |
| `softgate-0561a-hashi` | PASS | 2 | 2 | `0x0561A` 96 88 -> 8B 8C | none |
| `softgate-0562f-tatsuichi` | PASS | 4 | 4 | `0x0562F` 90 92 82 91 -> 89 98 8E 90 | none |
| `softgate-05643-heishichi` | PASS | 4 | 4 | `0x05643` 9D 82 8C 91 -> 8D 8E 8F 90 | none |
| `softgate-0569d-hashi` | PASS | 2 | 2 | `0x0569D` A0 92 -> 8B 8C | none |
| `softgate-056da-hashi` | PASS | 1 | 1 | `0x056DA` 9A 8C -> 8B 8C | none |
| `softgate-0571c-hashi` | PASS | 2 | 2 | `0x0571C` 92 84 -> 8B 8C | none |
| `softgate-057d4-hashi` | PASS | 2 | 2 | `0x057D4` A6 98 -> 8B 8C | none |
| `softgate-0736a-raifu` | PASS | 3 | 3 | `0x0736A` BB 95 AF -> 96 8E 97 | none |
| `softgate-0739d-raifu` | PASS | 3 | 3 | `0x0739D` BB 95 AF -> 96 8E 97 | none |
| `softgate-dev-combined` | PASS | 23 | 23 | `0x0562F` 90 92 82 91 -> 89 98 8E 90<br>`0x05643` 9D 82 8C 91 -> 8D 8E 8F 90<br>`0x0561A` 96 88 -> 8B 8C<br>`0x0569D` A0 92 -> 8B 8C<br>`0x056DA` 9A 8C -> 8B 8C<br>`0x0571C` 92 84 -> 8B 8C<br>`0x057D4` A6 98 -> 8B 8C<br>`0x0736A` BB 95 AF -> 96 8E 97<br>`0x0739D` BB 95 AF -> 96 8E 97 | none |
| `softgate-quarantine-05644-katana` | PASS | 3 | 3 | `0x05644` 82 8C 91 -> 88 89 8A | none |
| `softgate-quarantine-06295-katana` | PASS | 3 | 3 | `0x06295` 82 8C 91 -> 88 89 8A | none |
| `softgate-quarantine-0631c-katana` | PASS | 3 | 3 | `0x0631C` 82 8C 91 -> 88 89 8A | none |
| `softgate-quarantine-0635a-katana` | PASS | 3 | 3 | `0x0635A` 82 8C 91 -> 88 89 8A | none |
| `softgate-quarantine-07227-katana` | PASS | 3 | 3 | `0x07227` 8A 94 99 -> 88 89 8A | none |

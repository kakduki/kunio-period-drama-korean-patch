# Full Pointer Forced Page Samples

Status: **PASS**

- Samples: `5`
- Distinct optimized pages: `5`
- Pages: `10,14,31,40,42`

| pointer | CPU | page | state | R1 | text pixels | background | result |
| ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | `$9FB4` | 10 | `0x0B` | `0x94` | True | True | PASS |
| 25 | `$A140` | 14 | `0x0F` | `0x9C` | True | True | PASS |
| 50 | `$A30A` | 40 | `0x29` | `0xD0` | True | True | PASS |
| 110 | `$A77C` | 31 | `0x20` | `0xBE` | True | True | PASS |
| 181 | `$AADA` | 42 | `0x2B` | `0xD4` | True | True | PASS |

Pointers 25, 50, and 110 skip their initial `F0` only in this forced
visual harness because that control depends on the original event index.
All five samples preserve the field background and pass text pixels,
page state, R1 mapping, source progression, and terminator checks.
This is representative page/font evidence, not event-control promotion.

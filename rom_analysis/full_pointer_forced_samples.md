# Full Pointer Forced Page Samples

Status: **PASS**

- Samples: `5`
- Distinct optimized pages: `5`
- Pages: `10,14,30,39,41`

| pointer | CPU | page | state | R1 | text pixels | background | result |
| ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | `$9FB4` | 10 | `0x0B` | `0x94` | True | True | PASS |
| 25 | `$A140` | 14 | `0x0F` | `0x9C` | True | True | PASS |
| 50 | `$A30A` | 39 | `0x28` | `0xCE` | True | True | PASS |
| 110 | `$A777` | 30 | `0x1F` | `0xBC` | True | True | PASS |
| 181 | `$AACF` | 41 | `0x2A` | `0xD2` | True | True | PASS |

Pointers 25, 50, and 110 skip their initial `F0` only in this forced
visual harness because that control depends on the original event index.
All five samples preserve the field background and pass text pixels,
page state, R1 mapping, source progression, and terminator checks.
This is representative page/font evidence, not event-control promotion.

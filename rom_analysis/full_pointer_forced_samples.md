# Full Pointer Forced Page Samples

Status: **PASS**

- Samples: `5`
- Distinct optimized pages: `5`
- Pages: `11,16,41,43,46`

| pointer | CPU | page | state | R1 | text pixels | background | result |
| ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | `$9FB4` | 11 | `0x0C` | `0x96` | True | True | PASS |
| 25 | `$A13E` | 16 | `0x11` | `0xA0` | True | True | PASS |
| 50 | `$A30B` | 41 | `0x2A` | `0xD2` | True | True | PASS |
| 100 | `$A6D0` | 46 | `0x2F` | `0xDC` | True | True | PASS |
| 181 | `$AAF4` | 43 | `0x2C` | `0xD6` | True | True | PASS |

Pointers 25, 50, and 100 skip their initial `F0` only in this forced
visual harness because that control depends on the original event index.
All five samples preserve the field background and pass text pixels,
page state, R1 mapping, source progression, and terminator checks.
This is representative page/font evidence, not event-control promotion.

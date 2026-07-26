# English Reference Font Slot Map

The English IPS is applied in memory only. This map records physical CHR slots
whose tile bitmaps changed, with special focus on the verified dialogue alphabet
codes `0x81-0x9A` (`A-Z`) at observed physical tiles `0x181-0x19A`.

## Constraint

- Physical 8 KiB CHR-bank coordinates; runtime MMC3 mapping still needs screen-context proof before a release patch.
- CHR bank size: `8192` bytes; tile size: `16` bytes.

## Letter-Code Coverage

| code | English | physical slots | CHR banks | glyph variants |
| --- | --- | ---: | --- | ---: |
| `0x81` | A | 1 | 7 | 1 |
| `0x82` | B | 1 | 7 | 1 |
| `0x83` | C | 1 | 7 | 1 |
| `0x84` | D | 1 | 7 | 1 |
| `0x85` | E | 1 | 7 | 1 |
| `0x86` | F | 1 | 7 | 1 |
| `0x87` | G | 1 | 7 | 1 |
| `0x88` | H | 1 | 7 | 1 |
| `0x89` | I | 1 | 7 | 1 |
| `0x8A` | J | 1 | 7 | 1 |
| `0x8B` | K | 1 | 7 | 1 |
| `0x8C` | L | 1 | 7 | 1 |
| `0x8D` | M | 1 | 7 | 1 |
| `0x8E` | N | 1 | 7 | 1 |
| `0x8F` | O | 1 | 7 | 1 |
| `0x90` | P | 1 | 7 | 1 |
| `0x91` | Q | 1 | 7 | 1 |
| `0x92` | R | 1 | 7 | 1 |
| `0x93` | S | 1 | 7 | 1 |
| `0x94` | T | 1 | 7 | 1 |
| `0x95` | U | 1 | 7 | 1 |
| `0x96` | V | 1 | 7 | 1 |
| `0x97` | W | 1 | 7 | 1 |
| `0x98` | X | 1 | 7 | 1 |
| `0x99` | Y | 1 | 7 | 1 |
| `0x9A` | Z | 1 | 7 | 1 |

## Changed CHR Banks

| CHR bank | ROM range | changed tiles | changed bytes | tile spans | alphabet slots |
| ---: | --- | ---: | ---: | --- | ---: |
| 1 | `0x22010-0x2400F` | 1 | 8 | 0x033 | 0 |
| 2 | `0x24010-0x2600F` | 38 | 281 | 0x002-0x004, 0x007-0x009, 0x014-0x01B, 0x020-0x021, 0x026, 0x029-0x02A, 0x032-0x034, 0x037-0x039, 0x03B, 0x046-0x048, 0x04A-0x04B, 0x056-0x058, 0x05D, 0x068-0x069, 0x06B | 0 |
| 7 | `0x2E010-0x3000F` | 181 | 1900 | 0x101-0x139, 0x150-0x159, 0x15C, 0x160-0x166, 0x169-0x16A, 0x16C, 0x178-0x179, 0x17C, 0x181-0x1B6, 0x1B8-0x1B9, 0x1BB, 0x1BD, 0x1C0-0x1CC, 0x1D1, 0x1D4, 0x1E0-0x1FA | 26 |
| 12 | `0x38010-0x3A00F` | 12 | 30 | 0x0C0-0x0C3, 0x0C5, 0x0C7, 0x0CA, 0x0CE, 0x0D2-0x0D5 | 0 |
| 15 | `0x3E010-0x4000F` | 8 | 67 | 0x0AF, 0x0B9, 0x0BB, 0x0BD, 0x1B2-0x1B5 | 0 |

## Use In Korean Patch Work

- The primary dialogue stream is verified on the opening scene as nametable tile codes;
  the physical `0x100 + code` formula names the selected pattern-table-1 tile.
- A Korean proof string may reuse an English letter-code slot only after every physical slot
  required by its target screen has been replaced with the same Korean glyph.
- This map does not authorize a broad CHR overwrite. It narrows the next trace and visual
  check to the exact slots already proven relevant by the working English patch.

# Font Expansion Readiness

This report checks whether the planned glyph batches can be built from the current `font/char_map.json` and `font/korean_font_8x16.bin` assets.

## Summary

- char_map entries: **265**
- font binary bytes: **8480**
- expected bytes from char_map: **8480**
- font binary covers char_map: **true**
- planned extra slots: **163**
- max prefix buildable extra glyphs: **46**

## Batch Readiness

| extra glyphs | rows ready total | newly ready rows | buildable now | missing glyphs | first missing | first missing tile |
| ---: | ---: | ---: | --- | ---: | --- | --- |
| 16 | 17 | 7 | true | 0 | - | - |
| 32 | 25 | 15 | true | 0 | - | - |
| 64 | 50 | 40 | false | 1 | 재 | 0x141 |
| 96 | 74 | 64 | false | 10 | 재 | 0x141 |
| 128 | 94 | 84 | false | 17 | 재 | 0x141 |
| 160 | 115 | 105 | false | 22 | 재 | 0x141 |

## First Blocked Batch: 64 Extra Glyphs

| glyph | tile | PRG byte (+0x7A) | rows needing it |
| --- | --- | --- | ---: |
| 재 | `0x141` | `0xC7` | 2 |

## Rule

- This does not promote any new text into the IPS.
- If a batch is blocked here, regenerate or extend font assets before building that glyph batch.
- Even when a glyph batch is buildable, ROM text replacement still needs byte evidence, runtime/screen evidence, and length/padding safety.

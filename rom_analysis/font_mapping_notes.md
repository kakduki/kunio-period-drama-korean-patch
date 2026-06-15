# Font mapping notes

These notes are based on local visual inspection of `CHR bank 07`.

The generated reference images are local-only and ignored by git:

- `rom_analysis/font/chr_bank_07_8x8_labeled.png`
- `rom_analysis/font/chr_bank_07_rows_100_13f.png`
- `rom_analysis/font/chr_bank_07_rows_1c0_1ff.png`

Structured exports derived from this map:

- `rom_analysis/chr_bank07_tile_map.json`
- `rom_analysis/chr_bank07_tile_map.md`

## CHR bank 07 observations

- The font is much clearer when rendered as `8x8` tiles, not paired `8x16` tiles.
- The hiragana block starts around tile `0x101`.
- The hiragana sequence has a gap at tile `0x11F`; `ま` starts at `0x120` and `ん` is at `0x12F`.
- The numeric/Latin block starts around tile `0x1C0`.
- CHR ROM starts at `ROM+0x20010`; the rendered 8KB CHR bank 07 range is `ROM+0x2E010-0x3000F`.
- This is still a CHR tile index map, not yet confirmed as the in-ROM text byte encoding. FCEUX tracing is still needed to connect PRG text bytes to these CHR tile indexes.

## Preliminary visible tile map

### Hiragana block

| Tile | Glyph |
| --- | --- |
| `0x101` | あ |
| `0x102` | い |
| `0x103` | う |
| `0x104` | え |
| `0x105` | お |
| `0x106` | か |
| `0x107` | き |
| `0x108` | く |
| `0x109` | け |
| `0x10A` | こ |
| `0x10B` | さ |
| `0x10C` | し |
| `0x10D` | す |
| `0x10E` | せ |
| `0x10F` | そ |
| `0x110` | た |
| `0x111` | ち |
| `0x112` | つ |
| `0x113` | て |
| `0x114` | と |
| `0x115` | な |
| `0x116` | に |
| `0x117` | ぬ |
| `0x118` | ね |
| `0x119` | の |
| `0x11A` | は |
| `0x11B` | ひ |
| `0x11C` | ふ |
| `0x11D` | へ |
| `0x11E` | ほ |
| `0x120` | ま |
| `0x121` | み |
| `0x122` | む |
| `0x123` | め |
| `0x124` | も |
| `0x125` | や |
| `0x126` | ゆ |
| `0x127` | よ |
| `0x128` | ら |
| `0x129` | り |
| `0x12A` | る |
| `0x12B` | れ |
| `0x12C` | ろ |
| `0x12D` | わ |
| `0x12E` | を |
| `0x12F` | ん |

### Numeric and Latin block

| Tile | Glyph |
| --- | --- |
| `0x1C0` | 0 |
| `0x1C1` | 1 |
| `0x1C2` | 2 |
| `0x1C3` | 3 |
| `0x1C4` | 4 |
| `0x1C5` | 5 |
| `0x1C6` | 6 |
| `0x1C7` | 7 |
| `0x1C8` | 8 |
| `0x1C9` | 9 |
| `0x1E1` | A |
| `0x1E2` | B |
| `0x1E3` | C |
| `0x1E4` | D |
| `0x1E5` | E |
| `0x1E6` | F |
| `0x1E7` | G |
| `0x1E8` | H |
| `0x1E9` | I |
| `0x1EA` | J |
| `0x1EB` | K |
| `0x1EC` | L |
| `0x1ED` | M |
| `0x1EE` | N |
| `0x1EF` | O |
| `0x1F0` | P |
| `0x1F1` | Q |
| `0x1F2` | R |
| `0x1F3` | S |
| `0x1F4` | T |
| `0x1F5` | U |
| `0x1F6` | V |
| `0x1F7` | W |
| `0x1F8` | X |
| `0x1F9` | Y |
| `0x1FA` | Z |

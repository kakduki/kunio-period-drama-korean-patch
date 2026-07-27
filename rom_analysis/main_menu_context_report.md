# Main Menu Context Evidence

Status: **PASS**

## Proven Context

- Base template: `0x1F2C1`, 128 bytes.
- CPU copy source: `0xF2B1-0xF330`.
- PPU destination: `0x2700-0x277F` (nametable 1, rows 24-27).
- Both captures use the fixed 1,906-frame menu route and finish with `lua_done`.

## Label Map

| id | base ROM offset | legacy tile row/column | English structural reference | Korean 16x16 candidate |
| --- | --- | --- | --- | --- |
| `items` | `0x1F2E3` | 25/2 | ITEMS | 물건 |
| `status` | `0x1F2EA` | 25/9 | STATUS | 상태 |
| `growth` | `0x1F2F1` | 25/16 | GROWTH | 성장 |
| `tech` | `0x1F2F8` | 25/23 | TECH | 기술 |
| `record` | `0x1F323` | 27/2 | SAVE | 기록 |
| `ally` | `0x1F32A` | 27/9 | ALLY | 동료 |
| `setting` | `0x1F331` | 27/16 | SETTNG | 설정 |
| `save` | `0x1F338` | 27/23 | SETUP | 저장 |

## Readability Layout

Each Korean syllable uses a 2x2 set of 8x8 tiles. The first four labels
move to rows 24-25 and the lower four to rows 26-27, so both menu lines
remain fully inside the 240-pixel frame. The original selector stays in
its existing row until its runtime movement is separately verified.

| id | Korean | column | top row | bottom row |
| --- | --- | ---: | ---: | ---: |
| `items` | 물건 | 2 | 24 | 25 |
| `status` | 상태 | 9 | 24 | 25 |
| `growth` | 성장 | 16 | 24 | 25 |
| `tech` | 기술 | 23 | 24 | 25 |
| `record` | 기록 | 2 | 26 | 27 |
| `ally` | 동료 | 9 | 26 | 27 |
| `setting` | 설정 | 16 | 26 | 27 |
| `save` | 저장 | 23 | 26 | 27 |

## Runtime Font Mapping

- MMC3 mapper verdict: **PASS**.
- background tile codes 0x80-0xBF map through the captured R1 page
- Captured R1: `0x3E` -> visible CHR 1 KiB page `0x3E` (Bank 7).
- Pixel-mask verdict: **UNKNOWN**.
- no single CHR page matches the captured glyph masks
- Matching 1 KiB CHR pages: `[]`.

The mapper result identifies the live font page. The pixel-mask result stays
advisory because a literal screenshot mask can include palette and raster effects.
A menu candidate must still clone or otherwise isolate the live page before
replacing declared Korean tile codes.

## Checks

- `base_lua_done`: PASS
- `reference_lua_done`: PASS
- `base_template_matches_display`: PASS
- `base_mirror_matches_display`: PASS
- `reference_template_matches_display`: PASS
- `reference_mirror_matches_display`: PASS
- `english_labels_match_reference`: PASS
- `base_mapper_resolves_visible_label_page`: PASS

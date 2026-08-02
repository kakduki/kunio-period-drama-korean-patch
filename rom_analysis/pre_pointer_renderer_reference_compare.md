# Pre-Pointer Renderer Reference Comparison

This compares the same bounded FCEUX route on the Japanese base, the IPS-applied English reference, and the clean Korean candidate.

## Result

- The runtime transform at CPU `$8205-$820C` is unchanged across all three ROMs.
- The English reference changes pre-pointer data, renderer-support data, pointer data, menu data, and CHR; it does not require a new runtime hook for this path.
- The Korean candidate keeps the same transform and therefore must be advanced through data encoding, font ownership, pointer relocation, and visual proof.
- This confirms that the long lead time is not caused by lacking an English reference; the hard part is the Korean glyph and multi-renderer ownership contract.

## ROMs

| ROM | MD5 |
| --- | --- |
| japanese_base | `0d406a85285b4de8468f0dab6aad5fe5` |
| english_reference | `63e1d902807981f524af97748cd99500` |
| korean_clean_candidate | `2fba4bae8c65c31a2ebd96c7ed0f7fc9` |

## Region Changes

| region | range | English vs Japanese | Korean vs Japanese | Korean vs English |
| --- | --- | ---: | ---: | ---: |
| renderer_support | `0x05288-0x052C8` | 27 | 0 | 27 |
| pre_pointer_text | `0x056BC-0x05D54` | 1470 | 465 | 1428 |
| pointer_table | `0x05DD4-0x05FC4` | 311 | 483 | 487 |
| pointer_dialogue | `0x05FC4-0x07767` | 5897 | 4057 | 5850 |
| growth_ui | `0x07894-0x078AB` | 20 | 0 | 20 |
| menu_labels | `0x07FB6-0x0800F` | 74 | 88 | 86 |
| runtime_transform_8205 | `0x08215-0x0821D` | 0 | 0 | 0 |

## Runtime Bytes

- Japanese: `85 11 b1 07 45 1e 85 12`
- English: `85 11 b1 07 45 1e 85 12`
- Korean: `85 11 b1 07 45 1e 85 12`
- Unchanged across all three: `True`

## Interpretation

The English patch is a usable structural reference, but its changed bytes are not a universal copy recipe. The Korean implementation should keep the shared runtime transform intact and validate each renderer family independently.

# English Patch Implementation Map

Status: structural reference only

This is a compact implementation guide distilled from the public Technos
Samurai: Downtown Special v1.00 IPS. The IPS and any patched ROM are inputs
only and are not stored in this repository.

## Verified Input

| item | value |
| --- | --- |
| Japanese base MD5 | 0d406a85285b4de8468f0dab6aad5fe5 |
| Reference IPS records | 99 |
| Final changed bytes | 12,582 |
| Changed PRG bytes | 10,295 |
| Changed CHR bytes | 2,286 |
| Main dialogue pointer entries | 248 |
| Changed dialogue pointer entries | 244 |

## High-Value Structural Regions

| Base ROM range | Bank | English-patch classification | Korean-patch use |
| --- | ---: | --- | --- |
| 0x05288-0x052C6 | PRG 1 | renderer support | Inspect before changing dialogue byte interpretation. |
| 0x0561B-0x056AF | PRG 1 | name table | Treat as a renderer family distinct from pointer dialogue. |
| 0x056BC-0x05D53 | PRG 1 | pre-pointer text | Catalog separately; it is not proven to use pointer-table rules. |
| 0x05DD4-0x05FC3 | PRG 1 | 248-entry pointer table | Primary ownership map for dialogue records. |
| 0x05FC4-0x07766 | PRG 1 | pointer-driven dialogue data | Build Korean records and relocation plans from this model. |
| 0x07894-0x078AA | PRG 1 | growth UI | Verify as a separate UI renderer. |
| 0x07FB6-0x07FEC | PRG 1 | menu or label expansion | Do not treat as automatically executable code space. |
| 0x07FF7-0x0800E | PRG 1 | menu or label expansion | Audit pointer ownership before using as relocation space. |
| CHR Bank 7 | CHR 7 | 181 changed tiles | Primary dialogue-font evidence, but not a blanket Korean allocation. |

## Dialogue Model Confirmed by the Reference

1. The table at 0x05DD4-0x05FC3 contains 248 little-endian CPU pointers in the
   Bank 1 CPU window.
2. The English patch changed 244 entries, demonstrating that a translated
   dialogue record can grow and move without preserving its original length.
3. In the verified dialogue family, codes 0x81-0x9A render English A-Z and
   correspond to observed physical CHR Bank 7 tiles 0x181-0x19A.
4. The record stream contains controls such as 0x00, 0xBB, 0xCA, 0xF8, and
   0xFF. They must remain explicit tokens; none may be silently reclassified
   as ordinary Korean glyph data.
5. The reference moves individual records across the Bank 1 data area. A
   Korean compiler must therefore track every record owner and update only
   declared pointers.

## What the Reference Does Not Prove

- Japanese base-ROM glyph values have not yet been fully decoded.
- Every menu, status, item, and event surface does not necessarily use the
  same renderer as the pointer dialogue family.
- Every physical tile changed in English Bank 7 is not automatically safe for
  Korean dialogue.
- English localization wording is not Korean translation source material.
- English code changes are not safe to copy into the Korean patch.

## Required Korean Follow-Through

| English observation | Required Korean action |
| --- | --- |
| Pointer relocation is viable | Build a catalog-driven allocator and a changed-pointer allowlist. |
| A-Z occupies a known dialogue code pool | Measure a Korean code pool without consuming controls. |
| Bank 7 supplies dialogue tiles | Trace the screen-context bank mapping before expanding Korean tiles. |
| Multiple PRG text regions were changed | Keep renderer families separate in the catalog and verification queue. |
| English edits include non-text regions | Audit changes by ownership, not by byte appearance alone. |

The machine-readable sources remain rom_analysis/english_patch_record_map.csv,
rom_analysis/english_pointer_map.json, and rom_analysis/english_font_slot_map.json.

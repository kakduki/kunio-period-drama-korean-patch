# Full Korean Composed Candidate

## Candidate Identity

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- English reference ROM MD5: `63e1d902807981f524af97748cd99500`.
- Candidate ROM: `output/full_korean_items_title_none_nonpointer_candidate/kunio_period_drama_korean_expanded_nonpointer_candidate.nes`.
- Candidate MD5: `5f348772bb6809b1df0e7f84ef2e7603`.
- Release status: `NOT_READY`; this is a bounded development candidate.

## Composition Pipeline

1. Full pointer/menu base: `d062b19d23050cd4e148e22fbfff57b7`.
2. Direct-low UI with Items reservations: `b453fdef1c17ca3875fbd48b31454b5f`.
3. Items action owner chain: `b53f2f5ef066f69fac5998b99b2d35fa`.
4. Items name/title/NONE owners: `c032b78da7340abdc739058a706fdb2b`.
5. Eight non-pointer records and 18 Korean 8x8 slots: final candidate above.

The direct-low allocator reserves `0x20-0x27` for the Items title/NONE R0
glyphs and `0x38` for the title/NONE trailing blank. This prevents the earlier
collision where the direct-low menu assigned those same slots to other Korean
glyphs.

## Owner Evidence

| Context | Owner chain | Result |
| --- | --- | --- |
| Pointer dialogue | English pointer table and relocated Bank 1 records | 244 active rows compiled; forced page/runtime evidence exists |
| Items actions | ROM `0x13727` -> CPU `$B717` -> SRAM `$6360` -> PPU `$2363` | source and queue byte proof PASS |
| Items name/title | ROM `0x0561B`, CHR `0x3FB32`, suffix `0x136F4` | source and queue byte proof PASS |
| Items NONE | ROM `0x0FC31` -> SRAM `$6506` -> Items row 8 | source and queue byte proof PASS |
| Non-pointer screen family | eight equal-length PRG records from the bounded frame-883 evidence | 8/8 active on the current route at frame 362 |

The ninth historical non-pointer record at `0x0561A` is intentionally skipped:
it overlaps the Items name seed at `0x0561B`. Applying both would overwrite the
verified Korean name chain, so the overlap is classified as `DEFERRED_OWNER_OVERLAP`
instead of being silently patched.

## Runtime Gates

- Items bounded FCEUX capture: `PASS_BYTE_PROOF_VISUAL_UNKNOWN`.
- Items queue frame: `1737`; capture completion: frame `1906`.
- Final input explorer: finite completion at frame `1200`, five unique screen fingerprints,
  manual-style captures at frames `122`, `362`, `656`, `907`, and `1147`.
- Final non-pointer target records: `8/9` active at frame `362`; the missing row is the
  intentionally skipped overlap at `0x0561A`.
- Native GD screenshot pixels: `UNKNOWN_NATIVE_GDSCREENSHOT_TRANSPARENT`.
- Natural enemy-clear/boss route: `UNKNOWN`; no claim is made from the bounded input route.
- Broad pre-pointer coverage: `NOT_READY`; static English offsets are not promoted without
  display-owner proof.

## Realtime Translation Alternative

An AI subtitle overlay remains a useful immediate play aid because it does not require
ROM modification and can follow the natural boss route. It is not a replacement for this
patch pipeline: OCR can misread 8-bit fonts, translation adds latency, and fixed UI labels
are easily mistaken for dialogue. Treat it as a parallel usability track while the ROM
candidate continues through native screenshot and natural-route gates.

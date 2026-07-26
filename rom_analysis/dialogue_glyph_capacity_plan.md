# Dialogue Glyph Capacity Plan

Status: **PROOF_POOL_ONLY**

The opening proof proves an 8x16 Korean glyph in the live dialogue window. It
does not yet prove a final, whole-game Korean glyph capacity.

## Proven Now

| item | result | evidence |
| --- | --- | --- |
| Dialogue source record | Pointer 182 at ROM `0x071B6` / CPU `$B1A6` | bounded renderer trace and target record capture |
| Renderer layout | one source byte produces an existing vertical two-tile pair | queue trace and native capture |
| Korean 8x16 glyphs | 17 unique glyphs in the opening proof | `font_readability_gate.md` |
| English-reference code area | `0x81-0x9A` maps to Bank 7 physical tiles `0x181-0x19A` | `english_font_slot_map.md` |
| Current allocator pool | 17 codes: `0x81-0x89`, `0x8C-0x93` | `compile_korean_scene_batch.py` |

`0x8A` and `0x8B` stay reserved because the current renderer experiment did
not prove their branch behaviour for the 8x16 helper. The source proof itself
uses `0x81-0x89` and `0x8C-0x93`, including newly captured top/bottom pairs
for `0x92/0xB2` and `0x93/0xB3`.

## Not Proven Yet

- Whether codes `0x94-0x9A` can safely enter the 8x16 helper.
- Whether their corresponding bottom tiles can be replaced without affecting
  another screen or renderer family.
- A single font arrangement large enough for all Korean dialogue, menus, and
  labels in one released ROM.
- Pointer relocation and record growth rules for Korean text that does not fit
  an original record.

The original Japanese font map contains additional physical tiles, but that is
not permission to overwrite them. A physical tile listing alone does not show
its runtime renderer, control-code role, or screen context.

## Controlled Expansion Procedure

1. Choose one unapproved source code and its physical top/bottom CHR pair.
2. Build a one-record candidate with no other new text changes.
3. Run the same frame-883 bounded capture; require `lua_done`, exact target
   record bytes, and a native screenshot.
4. Mark the pair `PASS`, `FAIL`, or `UNKNOWN` with its ROM offsets and screen
   context.
5. Only `PASS` pairs may be added to the compiler allocator.

Until this table has more passing pairs, a batch with more than 17 unique
Korean glyphs is a deliberate compiler error rather than a risky ROM build.

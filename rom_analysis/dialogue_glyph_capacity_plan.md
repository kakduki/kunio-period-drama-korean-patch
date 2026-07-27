# Dialogue Glyph Capacity Plan

Status: **OPENING_18_GLYPH_POOL_SPEAKER_SEPARATOR_AND_RELOCATION_PROVEN**

This document records only what the fixed opening route proves. It is not a
whole-game font allocation or release approval.

## Proven In The Opening Route

| item | result | evidence |
| --- | --- | --- |
| Dialogue source record | PASS: pointer 182 at ROM `0x071B6` / CPU `$B1A6` | bounded target capture |
| Renderer layout | PASS: two native vertical 8x16 cells can form one Korean 16x16 syllable | renderer trace and native capture |
| Tier 1 source pool | PASS: 13 Korean syllables / 26 source slots `0x81-0x9A` | `opening_dialogue_16x16_capacity_tier1_capture/` |
| Tier 2 source pool | PASS: 17 Korean syllables / 34 source slots `0x81-0x9A` plus `0xC0-0xC7` | `opening_dialogue_16x16_capacity_tier2_capture/` |
| Expanded primary record | PASS: 45-byte pointer-182 record, all 45 runtime reads match at frame 883 | `opening_dialogue_16x16_relocation_proof_capture/` |
| Speaker separator surrogate | PASS: local paired 16x16 colon avoids the renderer-special raw `0xBB` byte; 47/47 runtime reads match at frame 883 | `opening_dialogue_16x16_speaker_separator_proof_capture/` |
| Pointer 183 preservation | STATIC PASS: original 21-byte record copied from `0x071DB` to `0x07FF6` / `$BFE6`; table entry 183 changes from `$B1CB` to `$BFE6` | `opening_dialogue_16x16_relocation_proof.json` |
| Pointer 183 display | UNKNOWN: its own event context has not been captured | no claim beyond static preservation |

## Static Page Lifecycle Evidence

| candidate | mapper lifecycle | runtime mapping | visual result | verdict |
| --- | --- | --- | --- | --- |
| `opening_dialogue_bank8_static_r1_page_proof` | normal setup `R1=3E -> 46` | `28/28` | dialogue-only black frame | FAIL_STATIC_R1_VISUAL_BACKGROUND |
| `opening_dialogue_bank8_static_r1_capacity_tier2` | normal setup `R1=3E -> 46` | FAIL: declared Bank-7 targets differ from Bank-8 runtime slots | background lost; dialogue-only capture | FAIL |
| `opening_dialogue_bank8_static_r1_safe_capacity_tier2` | normal setup `R1=3E -> 46`; actual R1 `0x800`-byte window clone | `67/67` | opening background and expanded Korean-looking dialogue visible | SOFT_GATE_PASS |

The small static page's mapping audit was useful but its visual gate failed.
The safe tier-2 candidate is the current page-lifecycle reference: it clones
the actual R1 window, preserves Bank 7, and writes the expanded glyphs to the
runtime Bank 8 slots. This remains an opening-context proof only.

The English IPS validates the ownership of source slots `0x81-0x9A` and shows
that this dialogue family already uses pointer relocation. Korean glyph pixels,
the code-cave helper, and Korean wording are generated locally; no English ROM
or IPS is included in the repository.

## Current Opening Candidate

The newest bounded candidate renders:

```text
쿠니마사: 어서 움직여!
분조 두목이 큰일이야!
```

It is a 47-byte, context-checked capacity and relocation proof. The original
raw `0xBB` speaker separator is intentionally absent from this Korean record:
a local paired 16x16 colon uses `0xC8,0xC9` instead. This proves readable
speaker separation on the opening screen, not a universal raw-`0xBB` decoder.

## Verification Contract

Every opening candidate uses the same route:

1. Run only the known input sequence to the opening dialogue.
2. Capture at frame 883.
3. Stop when Lua writes `lua_done`; do not continue into free gameplay.
4. Require matching target reads, a native screenshot, and a scoped byte audit.

For the current candidate, the result is `47/47` matching target reads,
`lua_done`, a readable native screenshot, and no visible opening background or
UI damage. The neighbouring record remains `STATIC_PASS_RUNTIME_UNKNOWN` until
its actual scene is reached by a bounded route, save state, or debug state.

## Still Open

- A persistent glyph strategy for all dialogue scenes rather than one
  scene-local 17-syllable pool.
- A release-wide speaker/control-token model. The current colon glyph is a
  visible surrogate for one record and does not replace raw `0xBB` decoding.
- Pointer-growth rules beyond one explicitly audited neighbour and code-cave
  tail.
- Menu, status, item, and event/boss text renderers, each with its own target
  route and font evidence.

No other Shift-JIS-like bytes, CHR slots, or pointer records inherit this pass.

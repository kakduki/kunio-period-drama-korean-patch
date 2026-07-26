# Dialogue Glyph Capacity Plan

Status: **OPENING_17_GLYPH_POOL_AND_RELOCATION_PROVEN**

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
| Pointer 183 preservation | STATIC PASS: original 21-byte record copied from `0x071DB` to `0x07FF6` / `$BFE6`; table entry 183 changes from `$B1CB` to `$BFE6` | `opening_dialogue_16x16_relocation_proof.json` |
| Pointer 183 display | UNKNOWN: its own event context has not been captured | no claim beyond static preservation |

The English IPS validates the ownership of source slots `0x81-0x9A` and shows
that this dialogue family already uses pointer relocation. Korean glyph pixels,
the code-cave helper, and Korean wording are generated locally; no English ROM
or IPS is included in the repository.

## Current Opening Candidate

The bounded candidate renders:

```text
쿠니마사 어서 움직여!
분조 두목이 큰일이야!
```

It is a 45-byte, context-checked capacity and relocation proof. The current
helper range deliberately excludes the renderer-special speaker byte `0xBB`,
so the speaker separator is not yet part of this candidate. That keeps the
result useful without pretending it is final release text.

## Verification Contract

Every opening candidate uses the same route:

1. Run only the known input sequence to the opening dialogue.
2. Capture at frame 883.
3. Stop when Lua writes `lua_done`; do not continue into free gameplay.
4. Require matching target reads, a native screenshot, and a scoped byte audit.

For the current candidate, the result is `45/45` matching target reads,
`lua_done`, a readable native screenshot, and no visible opening background or
UI damage. The neighbouring record remains `STATIC_PASS_RUNTIME_UNKNOWN` until
its actual scene is reached by a bounded route, save state, or debug state.

## Still Open

- A persistent glyph strategy for all dialogue scenes rather than one
  scene-local 17-syllable pool.
- A helper layout that supports both the `0x81-0x9A` / `0xC0-0xC7` allocation
  and the `0xBB` speaker separator without intercepting it.
- Pointer-growth rules beyond one explicitly audited neighbour and code-cave
  tail.
- Menu, status, item, and event/boss text renderers, each with its own target
  route and font evidence.

No other Shift-JIS-like bytes, CHR slots, or pointer records inherit this pass.

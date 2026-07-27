# Pointer Dialogue Batch 000-002 Direct 8x16 Candidate

Status: **CANDIDATE_BUILT_RUNTIME_UNKNOWN**

This is a soft-gate candidate, not a release patch. It compiles only
pointers 0, 1, and 2 from the Korean semantic draft, using the English
patch for pointer ownership and record placement structure.

## Scope

- Batch: `pointer_dialogue_batch_000_002_8x16`; pointer indices: `[0, 1, 2]`.
- Direct 8x16 glyphs: `24` in source range `0x81-0x98`.
- Packed record window: `0x05FE7` to `0x0601B`; protected next record: `0x06022`.
- Each candidate record uses the conservative `F0 BB 00 ... CA FF` shape.
- p0 has multiple source messages in the original record; this first candidate compacts its draft to one message and therefore remains structurally risky.

| pointer | old CPU | new CPU | encoded bytes | Korean draft |
| ---: | ---: | ---: | ---: | --- |
| 0 | `0x9FD7` | `0x9FD7` | 30 | 그래 싸워라! 나와 싸우지 않으면 못 지나간다 |
| 1 | `0x9FF9` | `0x9FF5` | 8 | 젠장! |
| 2 | `0xA004` | `0x9FFD` | 14 | 아, 또 만났군! |

## Candidate

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `ba3ef60856e1d2b5aa4dba40bcf1ff41`.
- ROM: `output/pointer_dialogue_batch_000_002_8x16/kunio_period_drama_korean_pointer_dialogue_batch_000_002_8x16.nes`.
- IPS: `output/pointer_dialogue_batch_000_002_8x16/kunio_period_drama_korean_pointer_dialogue_batch_000_002_8x16.ips`.
- Changed spans: `11`; escaped bytes: `0`.

## Runtime Gate

- Overall verdict: **UNKNOWN**.
- Boot smoke: **PASS** at frame `883` (`lua_done`).
- Pointer route probe: **UNKNOWN** at frame `5000` (`target_not_seen`).
- Route phase: `3`; watcher hits: `216`; final screen fingerprint: `8507662:16320`.
- p0, p1, and p2 were not fully matched. This is a route-evidence gap, not proof that the candidate text is displayed.
- The candidate remains a soft-gate build because p0 was compacted from a multi-message source record and no native-screen visual proof exists.

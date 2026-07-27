# Pointer Dialogue Batch 002-003

Status: **CANDIDATE_BUILT_RUNTIME_UNKNOWN**

This is a soft-gate candidate, not a release patch. It applies two
English-reference-guided Korean dialogue records outside the opening.
PTR-003 is deliberately relocated and its pointer is updated.

## Scope

- Batch: `pointer_dialogue_ptr_002_003`.
- Glyph pairs: `15`; source ranges: `['0x81-0x9A', '0xC0-0xC3']`.
- Renderer helper: `88` bytes at `0xBFA5`.
- Controls remain explicit; English wording is not written to the ROM.

| pointer | old CPU | new CPU | ROM record | encoded bytes | Korean draft | runtime |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 2 | `0xA004` | `0xA004` | `0x06014` | 13 | 아 또 만나! | UNKNOWN |
| 3 | `0xA012` | `0xA011` | `0x06021` | 50 | 그 녀석들 기억해? 저놈들이야! | UNKNOWN |

## Candidate

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `863c62ba178973ee1a96cc7971512149`.
- IPS: `output/pointer_dialogue_batch_002_003/kunio_period_drama_korean_pointer_dialogue_batch_002_003.ips`.
- Changed spans: `95`; escaped bytes: `0`.

## Runtime Gate

- Verdict: **UNKNOWN**.
- Reason: the bounded FCEUX target for this early-boss dialogue has no
  proven route or save-state entry yet. This avoids returning to an
  untargeted opening/title loop.

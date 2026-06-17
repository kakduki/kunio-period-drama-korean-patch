# v0.4 / Broad Candidate Conflicts

This report compares v0.4 applied PRG edits with broad-scan promotion candidates.

## Summary

- v0.4 applied edits: **13**
- Broad promotion candidates: **7**
- Overlapping conflicts: **3**
- High-confidence conflicts: **3**
- Non-overlapping broad candidates: **4**

## Conflicts

| broad ROM/span | broad meaning | confidence | v0.4 ROM/span | v0.4 meaning | decision |
| --- | --- | --- | --- | --- | --- |
| `0x06294` `0x06294-0x06297` | へいしち -> 헤이시치 | high | `0x06295` `0x06295-0x06297` | カタナ -> 카타나 | manual screen proof required before keeping either interpretation |
| `0x06359` `0x06359-0x0635C` | へいしち -> 헤이시치 | high | `0x0635A` `0x0635A-0x0635C` | カタナ -> 카타나 | manual screen proof required before keeping either interpretation |
| `0x0631B` `0x0631B-0x0631E` | へいしち -> 헤이시치 | high | `0x0631C` `0x0631C-0x0631E` | カタナ -> 카타나 | manual screen proof required before keeping either interpretation |

## Non-Overlapping Broad Candidates

| ROM/span | source | korean | confidence | original bytes | new glyphs |
| --- | --- | --- | --- | --- | --- |
| `0x052A5` `0x052A5-0x052A7` | たつじ | 타츠지 | medium | `82 84 7E` | 지 |
| `0x0440C` `0x0440C-0x0440E` | かじや | 대장간 | medium | `CA D0 E9` | 대간 |
| `0x05BE5` `0x05BE5-0x05BE7` | たつじ | 타츠지 | medium | `97 99 93` | 지 |
| `0x048F4` `0x048F4-0x048F6` | たつじ | 타츠지 | medium | `07 09 03` | 지 |

## Rule

- Do not build v0.5 by simply adding broad candidates on top of v0.4.
- Overlapping records indicate ambiguous static interpretation; manual screen evidence decides.
- If a broad candidate is confirmed, the conflicting v0.4 edit may need to be replaced or removed.

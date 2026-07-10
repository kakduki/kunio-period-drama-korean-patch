# English-reference static leads for Korean targets

> These are physical byte-diff and mapper-unknown pointer-search leads. They are not CPU-read, renderer, visual, or release evidence.

- Verified base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Verified English IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`
- Static leads: **5**

| task | offset | source → Korean | base bytes | English bytes | overlap | pointer candidates |
|---:|---|---|---|---|---:|---:|
| 3 | `0x052A5` | たつじ → 타츠지 | `82 84 7E` | `8F 00 7E` | 2B | 4 |
| 4 | `0x05BE5` | たつじ → 타츠지 | `97 99 93` | `93 95 8E` | 3B | 4 |
| 5 | `0x06294` | へいしち → 헤이시치 | `9D 82 8C 91` | `93 88 8F 97` | 4B | 4 |
| 6 | `0x0631B` | へいしち → 헤이시치 | `9D 82 8C 91` | `FF F0 BB 00` | 4B | 4 |
| 7 | `0x06359` | へいしち → 헤이시치 | `9D 82 8C 91` | `8F 8E 87 00` | 4B | 4 |

## Hard limits

- A changed English byte at the same file offset establishes only physical-diff overlap.
- Each 8KiB PRG location has four possible CPU-window representations. The scan records raw little-endian occurrences; it does not establish mapper state, opcode semantics, or a live pointer table.
- No Korean IPS/ROM is generated or modified by this artifact.

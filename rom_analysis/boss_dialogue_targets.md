# Boss Dialogue Targets

This queue is derived from the structural English-reference dump and the Korean draft.
It identifies likely boss-related pointer records without redistributing the reference script.

- Target records: **10**
- Natural route status: **UNKNOWN** for every row
- Release rule: a forced pointer render is not natural event proof

| pointer | pointer ROM | CPU | record ROM | Korean draft | status |
| ---: | --- | --- | --- | --- | --- |
| 020 | `0x05DFC` | `0xA1E7` | `0x061F7` | 진로 큰두목이 네놈들을 혼내라고 나를 보냈다 | UNKNOWN |
| 024 | `0x05E04` | `0xA263` | `0x06273` | 그래, 네가 큰두목이군 | UNKNOWN |
| 035 | `0x05E1A` | `0xA3BA` | `0x063CA` | 진로 큰두목이 널 손봐 주마 | UNKNOWN |
| 077 | `0x05E6E` | `0xA823` | `0x06833` | 대장님, 이 일의 배후에는 큰두목이 있다 | UNKNOWN |
| 079 | `0x05E72` | `0xA87C` | `0x0688C` | 큰두목이 고맙다고 전하더군 | UNKNOWN |
| 081 | `0x05E76` | `0xA8C7` | `0x068D7` | 내가 큰두목이다. 난 악당이고 강하지 | UNKNOWN |
| 101 | `0x05E9E` | `0xAB40` | `0x06B50` | 큰두목이 이것을 주셨다 | UNKNOWN |
| 102 | `0x05EA0` | `0xAB5B` | `0x06B6B` | 안 돼! 큰두목님 | UNKNOWN |
| 174 | `0x05F30` | `0xAFF8` | `0x07008` | 큰두목에게 확인하고 가야겠어 | UNKNOWN |
| 188 | `0x05F4C` | `0xB29C` | `0x072AC` | 아사지, 조용히 해. 두목님이 기다리신다 | UNKNOWN |

## Next Capture Rule

Use these records to classify a screen only after the route reaches the corresponding event naturally.
Do not promote a row from UNKNOWN using a forced pointer write alone.

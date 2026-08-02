# Tatsuji Clean Probe

- Status: `BUILT_SINGLE_STRING_SOFT_GATE_PROBE`.
- Candidate MD5: `38e0d4bc160006e68669520bfef92d4c`.
- Test string: `타츠지`.
- Release status: `NOT_READY`; visible boss/name screen proof is pending.

## Owners

| ROM offset | old bytes | new bytes | context |
| --- | --- | --- | --- |
| `0x048F4` | `07 09 03` | `89 98 A1` | boss/name label; visual route pending |
| `0x052A5` | `82 84 7E` | `89 98 A1` | boss/name label; visual route pending |
| `0x05BE5` | `97 99 93` | `89 98 A1` | boss/name label; visual route pending |

## Font Contract

| glyph | code | top ROM offset | bottom ROM offset |
| --- | --- | --- | --- |
| 타 | `0x89` | `0x2F8A0` | `0x2FAA0` |
| 츠 | `0x98` | `0x2F990` | `0x2FB90` |
| 지 | `0xA1` | `0x2FA20` | `0x2FC20` |

The probe is an isolated soft-gate build. It is not a final Korean patch.

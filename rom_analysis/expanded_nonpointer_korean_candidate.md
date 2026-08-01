# Expanded Non-Pointer Korean Candidate

Candidate built from the full pointer/menu ROM using nine equal-length PRG targets and the 18 allocated 8x8 Korean glyph slots.

- Input MD5: `d062b19d23050cd4e148e22fbfff57b7`.
- Candidate MD5: `12baf49a9b08a0a93b7f2d0e3140289c`.
- Selected PRG targets: `9`.
- Korean glyph slots copied: `18`.
- IPS records: `44`.
- Build status: `PASS`; IPS round trip: `PASS`.
- Visual status: pending the bounded frame-883 route on this composed candidate.
- Release status: `NOT_READY`.

## PRG Targets

| label | ROM offset | old bytes | new bytes | evidence |
| --- | --- | --- | --- | --- |
| Hashi | 0x0561A | 96 88 | 8B 8C | real frame-883 dialogue screen target record |
| Tatsuichi | 0x0562F | 90 92 82 91 | 89 98 8E 90 | real frame-883 dialogue screen target record |
| Heishichi | 0x05643 | 9D 82 8C 91 | 8D 8E 8F 90 | real frame-883 dialogue screen target record |
| Hashi | 0x0569D | A0 92 | 8B 8C | real frame-883 dialogue screen target record |
| Hashi | 0x056DA | 9A 8C | 8B 8C | real frame-883 dialogue screen target record |
| Hashi | 0x0571C | 92 84 | 8B 8C | real frame-883 dialogue screen target record |
| Hashi | 0x057D4 | A6 98 | 8B 8C | real frame-883 dialogue screen target record |
| Raifu | 0x0736A | BB 95 AF | 96 8E 97 | real frame-883 dialogue screen target record |
| Raifu | 0x0739D | BB 95 AF | 96 8E 97 | real frame-883 dialogue screen target record |

## Interpretation

The nine PRG spans are equal-length and were observed in the real frame-883 dialogue target record set. This candidate still needs exact screenshot/PPU proof on the composed ROM and does not prove the natural boss route.
## Bounded Runtime Comparison

- The candidate builds and IPS round trip pass.
- The stage progression probe reaches combat and late event-like captures, then ends with lua_done.
- The input explorer does not reproduce the historical frame-883 target screen on this current composed route. The current composed candidate and this expanded candidate both show only two unique screens by frame 1000 and then write a finite done row.
- Therefore the exact visual proof for the nine changed PRG strings remains UNKNOWN. The nine targets are not promoted to release status, and the route issue is recorded separately from the candidate byte changes.
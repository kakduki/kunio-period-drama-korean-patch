# Expanded Non-Pointer Korean Candidate

Candidate built from kunio_period_drama_korean_full_items_title_none_candidate.nes using nine equal-length PRG targets and the 18 allocated 8x8 Korean glyph slots.

- Input MD5: `c032b78da7340abdc739058a706fdb2b`.
- Candidate MD5: `5f348772bb6809b1df0e7f84ef2e7603`.
- Selected PRG targets: `8`.
- Korean glyph slots copied: `18`.
- IPS records: `28`.
- Build status: `PASS`; IPS round trip: `PASS`.
- Visual status: pending the bounded frame-883 route on this composed candidate.
- Release status: `NOT_READY`.

## PRG Targets

| label | ROM offset | old bytes | new bytes | evidence |
| --- | --- | --- | --- | --- |
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

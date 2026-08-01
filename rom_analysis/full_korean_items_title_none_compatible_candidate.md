# Full Korean Items Title and NONE Candidate

- Status: `BUILT_ITEMS_TITLE_NONE_STATIC_PASS_RUNTIME_PENDING`.
- Release status: `NOT_READY`.
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Input action-candidate MD5: `b53f2f5ef066f69fac5998b99b2d35fa`.
- Candidate MD5: `c032b78da7340abdc739058a706fdb2b`.
- Runtime route: bounded Items menu capture at frame 1906; no opening-loop claim.

## English Owner Chains

| owner | source | runtime destination | new bytes |
| --- | --- | --- | --- |
| name_prg_seed | `0x0561B` | alternate PRG name seed | `A0 A1 A2 FF FF` |
| name_ppu_seed | `0x3FB32` | PPU-read name seed -> RAM $7AFB -> title prefix $60A8 | `A0 A1 A2 80 80` |
| title_suffix | `0x136F4` | RAM $60AD | `B6 A3 80 A4 A5 80 80 80 80 80 80 CD` |
| none | `0x0FC31` | RAM $6506 | `26 27 38 38 38` |

## Gate

- Static source scope: PASS.
- IPS round trip: PASS.
- FCEUX title/NONE byte proof: pending bounded runtime capture.
- Native Lua screenshot pixels: UNKNOWN because the available screenshot buffer is transparent.
- Release status: NOT_READY.

# Full Korean Items Title and NONE Candidate

- Status: `BUILT_ITEMS_TITLE_NONE_RUNTIME_BYTE_PASS_VISUAL_UNKNOWN`.
- Release status: `NOT_READY`.
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Input action-candidate MD5: `e706f34c16d5e38ab00c730b004d5d9f`.
- Candidate MD5: `2fba4bae8c65c31a2ebd96c7ed0f7fc9`.
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
- FCEUX title/NONE byte proof: PASS.
- Native Lua screenshot pixels: UNKNOWN because the available screenshot buffer is transparent.
- Release status: NOT_READY.

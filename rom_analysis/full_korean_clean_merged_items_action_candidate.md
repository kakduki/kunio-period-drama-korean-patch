# Full Korean Items Action Candidate

- Status: `BUILT_ITEMS_ACTION_STATIC_PASS_RUNTIME_UNKNOWN`.
- Release status: `NOT_READY`.
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `e706f34c16d5e38ab00c730b004d5d9f`.
- Source chain: ROM `0x13727` -> SRAM `$6360` -> PPU `$2363`.
- Font page: normal Items R1 `0x3E/0x3F`.

| English | Korean | ROM offset | new bytes |
| --- | --- | --- | --- |
| USE | 사용 | `0x1372B` | `8C 98 00` |
| REMOVE | 버리기 | `0x13733` | `99 9B 9C 00 00 00` |
| GIVE | 주기 | `0x1373B` | `9E 9C 00 00` |
| DRP | 버림 | `0x13743` | `99 A3 00` |

## Gate

- Byte-scope, source-chain, and IPS round-trip: PASS.
- Exact candidate Items PPU/source/queue proof: UNKNOWN.
- Title and empty-inventory rows remain untranslated and are separate follow-up owners.

# PTR-181 Conditional Mapper Runtime Report

Status: **PASS_DEVELOPMENT_PAGE_LIFECYCLE**

## Candidate

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `b5f326deabbbdf791d775e9e9b5ad7c0`
- Target: pointer 181, ROM `0x07198`, CPU `$B188`
- Target mapper: `R0/R1=3C/46`
- Normal mapper: `R0/R1=3C/3E`

The paired renderer sets `$07FF=1` only after matching PTR-181. The fixed-bank
mapper wrapper selects the Korean page only while that flag is set and screen
state `$51` is `0x13`. Any normal-context mapper call clears the flag and
executes the original `3C/3E` mapping.

## Bounded Evidence

| checkpoint | mapper | result |
| ---: | --- | --- |
| frame 392 | `3C/46` | Korean probe text visible; field background preserved |
| frame 622 | `3C/3E` | target scene exited; original page restored |
| frame 1315 | `3C/3E` | combat screen remains playable |
| frame 7073 | `3C/3E` | late menu screen visible, not black |
| frame 7200 | `3C/3E` | finite `lua_done`; 45 unique screens |

## Gate

| check | result |
| --- | --- |
| PTR-181 ownership | PASS |
| Korean target rendering | PASS |
| Automatic page restoration | PASS |
| 7200-frame route regression | PASS |
| Translation prose approval | NOT TESTED |
| Full 248-record page table | NOT IMPLEMENTED |
| Release candidate | NO |

This resolves the page-lifecycle failure for one verified dialogue context.
`$07FF` was zero in all 51 sampled base-route RAM dumps; broader routes must
still audit that byte before the mechanism is promoted to every scene.

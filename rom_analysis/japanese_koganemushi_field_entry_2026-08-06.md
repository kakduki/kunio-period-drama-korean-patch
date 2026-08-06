# Japanese Koganemushi Field Entry (2026-08-06)

## Scope

Reproduce the documented Koganemushi name-entry secret on the verified Japanese base, then observe the resulting game state using button input only. This is route evidence for later encounter-map work, not a ROM or RAM patch.

## Base and command

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Base SHA-256: `54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a`
- Probe: `lua/kunio_name_entry_probe.lua`
- Direction pulse: 1 frame
- A/B confirmation pulse: 8 frames
- Input gap: 20 frames
- No ROM, SRAM, or CPU-memory writes were performed.

## Evidence

| Frame | Observation | Classification |
|---:|---|---|
| 2145 | Japanese name-entry grid is rendered | PASS_NAME_ENTRY_SCREEN |
| 3600 | Entered Japanese name is visible in the name field | PASS_SECRET_INPUT_STATE |
| 3660 | Japanese setup screen is rendered after confirming the name | PASS_KOGANEMUSHI_ROUTE_EXIT |
| 4260 | Actual town/field screen is rendered with the large-money value visible | PASS_FIELD_ENTRY_AFTER_SECRET |
| 5200 | Bounded run completes with `lua_done`, 31 unique fingerprints | PASS_BOUNDED_COMPLETION |

The field capture includes the player at the left side of the town scene and Japanese shop/town labels. The visible money value is consistent with the documented secret, but this report does not promote a RAM address as the money owner.

## Open gates

The run does not prove Map CRSR ownership, direct map travel, enemy encounter, enemy defeat, boss spawn, or boss dialogue. The post-cheat menu timing used here did not produce a distinct map screen. These remain `UNKNOWN`; no cheat-state write or native patch was authorized.

## Reproduction

```powershell
python scripts\run_fceux_lua_analysis.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\kunio_name_entry_probe.lua --frames 5200 --timeout 300 --final-output C:\tmp\japanese_koganemushi_post_map_2026_08_06 --clean-output --no-dump-hex --no-dump-bin --lua-env KUNIO_NAME_SETUP_ROUTE=1 --lua-env KUNIO_KOGANEMUSHI=1 --lua-env KUNIO_POST_CHEAT_ROUTE=1 --lua-env KUNIO_CHEAT_DIRECTION_PULSE=1 --lua-env KUNIO_CHEAT_CONFIRM_PULSE=8 --lua-env KUNIO_CHEAT_GAP=20 --lua-env KUNIO_NAME_UNIQUE_LIMIT=100 --lua-env KUNIO_FORCE_CAPTURE_FRAME=3600 --lua-env KUNIO_FORCE_CAPTURE_GAP=30
```

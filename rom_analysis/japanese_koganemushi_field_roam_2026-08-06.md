# Japanese Koganemushi Field Roam (2026-08-06)

## Scope

After the Japanese Koganemushi route reaches the real town/field screen, send only bounded directional input to test whether the scene transitions to another region, shop, enemy encounter, or map. The roam mode does not send Start, B, or memory writes.

## Result

- Base route: Japanese Koganemushi field entry
- Run: `C:\tmp\japanese_koganemushi_field_roam_2026_08_06`
- Frames: 6,500
- Completion: `lua_done`
- Screen fingerprints: 31 unique total, no new fingerprint after the field state stabilized
- Late capture: frame 4440 shows the player at the left edge of the Japanese town/field scene
- Collision/defeat/boss evidence: none

The bounded directional sweep did not establish a field-to-field transition or an encounter. The unchanged scene may represent a movement boundary, a shop/interaction state, or an input timing/position issue. It is not evidence of a ROM hang because the Lua run completed and the emulator remained responsive.

## Classification

`PASS_CHEAT_FIELD_STATE; UNKNOWN_FIELD_MOVEMENT_AND_ENCOUNTER`

The new `KUNIO_POST_FIELD_ROAM=1` mode remains diagnostic only. No RAM address, cheat write, boss flag, or patch target was promoted.

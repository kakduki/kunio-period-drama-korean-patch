# Next Manual Run

This is the shortest current FCEUX action queue. It combines primary-patch visual review and v0.4.3 route proof work.

## Summary

- Pending actions: **12**
- Primary v0.4.2 visual checks: **9**
- v0.4.3 route proof checks: **3**
- Recommended phase: `primary_v042_visual_review`
- Rule: verify already-applied rows first, then prove new route candidates.

## Recommended Next Action

- Open ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Run Lua: `lua/kunio_manual_v042_capture_watch.lua`
- Target: `0x0569D`
- Group: `Hashi`
- Screen hint: look for a bridge/stage/location label
- Why: This row is already changed by the primary IPS, so visual review moves the current patch closer to release-readiness.
- If the visible screen is still the title/opening screen, stop with `Q` and manually change screens.
- If you launch with `python scripts/run_next_manual_fceux.py`, a new dump triggers the after-capture refresh automatically.
- If the visible screen matches the target, record the visual review after the dump has been refreshed.

Record matching visual review:

```powershell
python scripts/record_primary_visual_review.py 0x0569D --confirm --screen-context "look for a bridge/stage/location label visible"
```

After capture if you ran FCEUX/Lua directly instead of the launcher:

```powershell
python scripts/refresh_after_manual_capture.py --phase primary
```

## Full Queue

| priority | phase | target | group | ROM | watcher | hint |
| ---: | --- | --- | --- | --- | --- | --- |
| 20 | `primary_v042_visual_review` | `0x0569D` | Hashi | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a bridge/stage/location label |
| 30 | `primary_v042_visual_review` | `0x0561A` | Hashi | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a bridge/stage/location label |
| 30 | `primary_v042_visual_review` | `0x05643` | Heishichi | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a visible Heishichi name/dialogue context |
| 30 | `primary_v042_visual_review` | `0x057D4` | Hashi | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a bridge/stage/location label |
| 30 | `primary_v042_visual_review` | `0x0736A` | Raifu | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a life/status UI label |
| 30 | `primary_v042_visual_review` | `0x0739D` | Raifu | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a life/status UI label |
| 40 | `primary_v042_visual_review` | `0x0562F` | Tatsuichi | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a visible Tatsuichi name/dialogue context |
| 40 | `primary_v042_visual_review` | `0x056DA` | Hashi | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a bridge/stage/location label |
| 40 | `primary_v042_visual_review` | `0x0571C` | Hashi | `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes` | `lua/kunio_manual_v042_capture_watch.lua` | look for a bridge/stage/location label |
| 101 | `v043_candidate_proof` | `0x0440C` | Kajiya | `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes` | `lua/kunio_manual_route_kajiya_capture_watch.lua` | look for a blacksmith/shop or blacksmith-stage label |
| 102 | `v043_candidate_proof` | `0x048F4, 0x052A5, 0x05BE5` | Tatsuji | `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes` | `lua/kunio_manual_route_tatsuji_capture_watch.lua` | look for a visible Tatsuji boss/name context |
| 103 | `v043_candidate_proof` | `0x06294, 0x0631B, 0x06359` | Heishichi | `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes` | `lua/kunio_manual_route_heishichi_capture_watch.lua` | look for a visible Heishichi name/dialogue context |

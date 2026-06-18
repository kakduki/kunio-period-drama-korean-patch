# Current Primary Visual Task

- Decision: `NEEDS_MANUAL_VISUAL_PROOF`
- Target: `0x0569D` / Hashi
- ROM to open: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Watcher Lua: `lua/kunio_manual_v042_capture_watch.lua`
- Required screen: A patched-ROM screen where the Hashi bridge/stage/location label is visibly displayed.
- Existing auto-input byte match: `True`
- Existing auto-input context status: `CONTEXT_REJECTED_DIALOGUE_NOT_LOCATION_LABEL`
- Existing PNG: `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen.png`
- Existing target records: `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_target_records.tsv`
- Existing record snapshot: `85 8B 8C FF`
- Why not auto-approved: The existing auto-input PNG reaches an in-game dialogue/background scene; it is not a clear bridge/stage/location label screen.

## Commands

```powershell
python scripts/preflight_manual_fceux.py
python scripts/run_next_manual_fceux.py
python scripts/confirm_next_primary_visual.py --confirm-visible
```

Only run the confirm command after the patched-ROM screen visibly matches the required screen.
If FCEUX remains on the title/opening screen, stop the run instead of waiting longer.

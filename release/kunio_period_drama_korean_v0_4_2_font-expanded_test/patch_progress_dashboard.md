# Patch Progress Dashboard

Single-page status for the current Korean patch work.

## Current Patch

- Primary candidate: **v0.4.2 font-expanded**
- Primary IPS: `output\kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips`
- Expected patched MD5: `ea11dc002a1a7b07682ce00a754b1a61`
- Applied text rows: **10**
- Runtime-confirmed rows: **1**
- Static candidate rows: **8**

## Manual Evidence

- Pending manual actions: **13**
- Pending primary visual checks: **10**
- Pending v0.4.3 route proofs: **3**
- Checked-in manual dump record files: **0**

## v0.4.3 Gate

- Candidate rows: **7**
- CPU-read matches: **0**
- Visual confirmations: **0**
- Applied rows: **0**

## Next Action

- Phase: `primary_v042_visual_review`
- Target: `0x07227`
- Group: `Katana`
- ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Lua: `lua/kunio_manual_v042_capture_watch.lua`
- Hint: look for a katana/weapon item label
- After capture:
  - `python scripts/refresh_after_manual_capture.py --phase primary`

## Release Blockers

- Primary v0.4.2 rows still need visible-screen review.
- v0.4.3 candidates have no base-ROM CPU-read proof yet.
- v0.4.3 candidates have no visual-context confirmations yet.
- No checked-in manual FCEUX dump records exist yet.

## Useful Commands

```powershell
python scripts/preflight_manual_fceux.py
python scripts/run_next_manual_fceux.py
python scripts/confirm_next_primary_visual.py --confirm-visible
python scripts/prepare_next_manual_run.py --powershell
python scripts/refresh_after_manual_capture.py --phase primary
python scripts/refresh_after_manual_capture.py --phase broad
python scripts/run_project_checks.py
```

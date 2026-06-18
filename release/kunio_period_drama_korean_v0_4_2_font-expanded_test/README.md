# Kunio Period Drama Korean Patch v0.4.2 font-expanded Test

This is an incomplete manual-test IPS bundle, not a final release.

## Files

- `kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips`: primary IPS patch
- `patch_progress_dashboard.md`: one-page current status, blockers, and next action
- `patch_candidate_manifest.md`: candidate status and verification notes
- `primary_patch_contents.md`: readable list of the text rows currently changed by the primary IPS
- `primary_visual_checklist.md`: visual-review queue for rows already changed by the primary IPS
- `auto_input_evidence_report.md`: scripted-route PNG and byte-match evidence for v0.4.2 rows
- `auto_input_review_crops.md`: focused dialogue/overlay crops from scripted-route screenshots
- `auto_input_visual_triage.md`: current decision on which auto-input evidence can and cannot be used for visual approval
- `katana_visual_explorer_report.md`: focused route evidence that reaches the item list for the Katana visual target
- `patch_decision_matrix.md`: next manual verification priorities
- `manual_capture_cards.md`: short FCEUX tasks to avoid blind autoplay loops
- `next_manual_run.md`: single recommended next FCEUX action queue
- `manual_capture_status.md`: generated status of manual dump evidence
- `manual_dump_inventory.md`: inventory of manual dump folders, screenshots, and target records
- `manual_capture_workflow.md`: short manual FCEUX workflow with route watcher guidance
- `manual_proof_routes.md`: three grouped manual routes for the current seven screen-proof candidates
- `route_fceux_targets.md`: route-specific FCEUX watcher files for those three manual routes
- `route_proof_status.md`: current proof status for the three route-specific watchers
- `release_test_checklist.md`: short apply/capture/review checklist for this bundle
- `lua/`: FCEUX manual capture scripts and target tables for v0.4.2 and broad-scan proof
- `video_route_reference.md`: gameplay-video route reference for replacing blind autoplay with known paths
- `v042_manual_proof_packet.md`: seven focused base-ROM proof tasks for the next text candidates
- `broad_scan_manual_summary.md`: latest status of broad-scan manual dump evidence
- `broad_scan_visual_review.json`: manual visual-confirmation template for the v0.4.3 gate
- `v043_broad_verified_build_report.json`: current v0.4.3 gate result
- `v043_broad_verified_build_report.md`: readable current v0.4.3 gate result
- `v043_proof_status.md`: row-by-row CPU-read and visual-review gate status
- `kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified.ips`: optional manual-screen-test IPS, not a primary patch
- `kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified_report.md`: preview IPS contents and warnings
- `translation_pattern_scan.md`: broad ROM candidate scan against all 144 translation entries
- `translation_scan_capture_queue.md`: focused broad-scan capture queue with readable text labels
- `reference_capture_plan.md`: transcript/reference-guided manual screen priorities
- `broad_scan_patchability.md`: length-safe broad-scan candidates with v0.4.2 planned bytes
- `translation_glyph_coverage.md`: full translation glyph coverage against the current patch plan
- `next_glyph_expansion_plan.md`: prioritized glyph batches for future font expansion
- `font_expansion_readiness.md`: current font asset gate for planned glyph batches
- `batch46_text_readiness.md`: broad-scan text gate after the largest currently buildable font expansion
- `v042_text_promotion_readiness.md`: broad-scan text candidates now font-ready under v0.4.2
- `kunio_period_drama_korean_font_expansion_v0.5_batch32_report.md`: local font-only expansion candidate report
- `kunio_period_drama_korean_font_expansion_v0.5_batch46_report.md`: largest currently buildable font-only expansion candidate report
- `apply_ips_standalone.py`: standalone IPS applier for this bundle
- `record_primary_visual_review.py`: helper to mark primary v0.4.2 visual review rows after a manual screen check
- `record_visual_review.py`: helper to mark v0.4.3 broad-scan visual review rows after a manual screen check
- `refresh_after_manual_capture.py`: one-command report refresh after manual FCEUX capture
- `prepare_next_manual_run.py`: prints the next focused manual FCEUX setup
- `preflight_manual_fceux.py`: checks the next manual FCEUX inputs before launching the emulator
- `run_next_manual_fceux.py`: launches the current next manual FCEUX action after preflight checks
- `confirm_next_primary_visual.py`: records the current next primary visual row after the screen is visibly confirmed
- `convert_fceux_gd_to_png.py`: converts FCEUX `gui.gdscreenshot()` dumps into PNG review images
- `generate_auto_input_evidence_report.py`: rebuilds the auto-input evidence summary from checked-in capture records
- `generate_auto_input_review_crops.py`: rebuilds focused PNG crops from FCEUX `.gd` screenshots
- `generate_auto_input_visual_triage.py`: rebuilds the byte-match versus visual-approval decision report
- `generate_katana_visual_explorer_report.py`: rebuilds the Katana route evidence summary
- `SHA256SUMS.txt`: checksums for bundle files

## Required Base ROM

- Expected base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Use your own legally obtained Japanese ROM.
- Do not distribute ROM files.

## Expected Result

- Primary candidate: **v0.4.2 font-expanded**
- Expected patched MD5: `ea11dc002a1a7b07682ce00a754b1a61`

## Apply In Repository

From the repository root, after putting your base ROM in `rom/`:

```powershell
python scripts/apply_primary_patch.py --output output/kunio_period_drama_korean_v0.4.2_test_applied.nes
```

## Apply From This Bundle Only

From inside this extracted bundle folder:

```powershell
python apply_ips_standalone.py C:\path\to\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes
```

To apply the optional unverified broad preview IPS for manual screen comparison:

```powershell
python apply_ips_standalone.py C:\path\to\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes --ips kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified.ips
```

## FCEUX Manual Capture

Before opening FCEUX from the repository, run `python scripts/preflight_manual_fceux.py`.
To open the current next action directly from the repository, run `python scripts/run_next_manual_fceux.py`.
When that launcher detects a new dump, it runs the matching after-capture refresh automatically.
After the visible patched-ROM screen matches the target, run `python scripts/confirm_next_primary_visual.py --confirm-visible`.
Start with `next_manual_run.md`; it names the single recommended ROM, Lua watcher, target, and screen hint.
From the repository root, `python scripts/prepare_next_manual_run.py --powershell` prints the same focused setup.
From this extracted bundle folder, run `python prepare_next_manual_run.py --powershell`.

Copy or run the scripts from this bundle's `lua/` folder in FCEUX:

```text
lua/kunio_manual_v042_capture_watch.lua
lua/kunio_manual_broad_scan_capture_watch.lua
```

Press `D` on each manually reached target screen to save a dump; press `Q` to stop the watcher.
If the FCEUX window is still on the title/opening screen, stop instead of waiting.

If you ran FCEUX/Lua directly instead of `run_next_manual_fceux.py`, refresh a v0.4.2 primary-patch capture with:

```powershell
python scripts/refresh_after_manual_capture.py --phase primary
```

If you ran FCEUX/Lua directly for a base-ROM broad/route proof capture, refresh with:

```powershell
python scripts/refresh_after_manual_capture.py --phase broad
```

## Verify In Repository

From the repository root:

```powershell
python scripts/verify_primary_patch.py
python scripts/run_project_checks.py
```

## Current Limitations

- Still needs manual FCEUX screen verification.
- The broad preview IPS is not proof-approved and is only for manual screen comparison.
- v0.4 broad-scan conflicts are intentionally excluded from this candidate.
- Padding/shortened replacements are not included.

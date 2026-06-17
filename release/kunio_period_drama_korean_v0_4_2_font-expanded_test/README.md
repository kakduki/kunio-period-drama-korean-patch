# Kunio Period Drama Korean Patch v0.4.2 font-expanded Test

This is an incomplete manual-test IPS bundle, not a final release.

## Files

- `kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips`: primary IPS patch
- `patch_candidate_manifest.md`: candidate status and verification notes
- `patch_decision_matrix.md`: next manual verification priorities
- `manual_capture_cards.md`: short FCEUX tasks to avoid blind autoplay loops
- `manual_capture_status.md`: generated status of manual dump evidence
- `translation_glyph_coverage.md`: full translation glyph coverage against the current patch plan
- `next_glyph_expansion_plan.md`: prioritized glyph batches for future font expansion
- `kunio_period_drama_korean_font_expansion_v0.5_batch32_report.md`: local font-only expansion candidate report
- `apply_ips_standalone.py`: standalone IPS applier for this bundle
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

## Verify In Repository

From the repository root:

```powershell
python scripts/verify_primary_patch.py
python scripts/run_project_checks.py
```

## Current Limitations

- Still needs manual FCEUX screen verification.
- v0.4 broad-scan conflicts are intentionally excluded from this candidate.
- Padding/shortened replacements are not included.

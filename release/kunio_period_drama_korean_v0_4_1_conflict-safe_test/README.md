# Kunio Period Drama Korean Patch v0.4.1 Test

This is an incomplete manual-test IPS bundle, not a final release.

## Files

- `kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.ips`: primary IPS patch
- `patch_candidate_manifest.md`: candidate status and verification notes
- `patch_decision_matrix.md`: next manual verification priorities
- `SHA256SUMS.txt`: checksums for bundle files

## Required Base ROM

- Expected base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Use your own legally obtained Japanese ROM.
- Do not distribute ROM files.

## Expected Result

- Primary candidate: **v0.4.1 conflict-safe**
- Expected patched MD5: `2b9f569fa175c719333064b8d73bc273`

## Verify In Repository

From the repository root:

```powershell
python scripts/verify_primary_patch.py
python scripts/run_project_checks.py
```

## Current Limitations

- Still needs manual FCEUX screen verification.
- v0.4 broad-scan conflicts are intentionally excluded from this v0.4.1 candidate.
- Padding/shortened replacements are not included.

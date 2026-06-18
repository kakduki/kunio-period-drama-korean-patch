# Release Gate Checklist

Hard gates apply only to release candidates, not to soft-gated development builds.

## Gate Status Summary

| gate | status | failure class | evidence |
| --- | --- | --- | --- |
| development soft gate | PASS | none | selected/combined/quarantined candidate builds and boot smoke evidence are present |
| candidate patch scope constrained | PASS | none | patch_scope_audit.md verifies each softgate candidate only changes planned PRG spans |
| release-included visual proof | FAIL | VISUAL_PROOF_PENDING | primary v0.4.2 and softgate rows still require visible-screen proof before release |
| high-risk/quarantined visual proof | FAIL | HIGH_RISK_VISUAL_PROOF_PENDING | 5 quarantined Katana candidates require item-list visual proof |
| false-positive/ambiguous bytes excluded | PASS | none | quarantined candidates are isolated and not included in softgate-dev-combined |
| base and patched hashes documented | PASS | none | patched_rom_report.md records base MD5 and candidate MD5 values |
| IPS applies from clean base ROM | PASS | none | scripts/test_candidate_ips_apply.py applies each softgate IPS to the clean base ROM and checks candidate MD5 values |
| release zip contains no ROM | PASS | none | release/kunio_period_drama_korean_v0_4_2_font-expanded_test.zip contains no .nes entries |
| regression boot smoke | PASS | none | smoke_summary_*.tsv files report lua_done for candidate boot tests |
| shortened padding rule acceptance | UNKNOWN | PADDING_RULE_UNPROVEN | padding experiment CPU evidence exists, but strict PPU/visual acceptance is still missing |

## Development Soft Gate

- [x] Select one active string from one known screen/context.
- [x] Record ROM offset, PRG bank, bytes, and context.
- [x] Build a one-string candidate ROM/IPS.
- [x] Verify candidate ROMs only alter planned PRG spans.
- [x] Run emulator boot smoke test.
- [x] Classify result as PASS/FAIL/UNKNOWN.

## Release Hard Gate

- [ ] Manual visual proof for every release-included string.
- [ ] Manual visual proof for every high-risk/quarantined string before merging into the dev candidate.
- [ ] No known false-positive or ambiguous byte ranges patched.
- [ ] Base ROM hash and patched ROM hash documented.
- [ ] IPS applies cleanly from a clean base ROM.
- [ ] No `.nes` files in release zip.
- [ ] Regression smoke test passes on the release candidate.

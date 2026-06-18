# Release Gate Checklist

Hard gates apply only to release candidates, not to soft-gated development builds.

## Gate Status Summary

| gate | status | failure class | evidence |
| --- | --- | --- | --- |
| development soft gate | PASS | none | selected/combined/quarantined candidate builds and boot smoke evidence are present |
| release-included visual proof | FAIL | VISUAL_PROOF_PENDING | primary v0.4.2 and softgate rows still require visible-screen proof before release |
| high-risk/quarantined visual proof | FAIL | HIGH_RISK_VISUAL_PROOF_PENDING | 5 quarantined Katana candidates require item-list visual proof |
| false-positive/ambiguous bytes excluded | PASS | none | quarantined candidates are isolated and not included in softgate-dev-combined |
| base and patched hashes documented | PASS | none | patched_rom_report.md records base MD5 and candidate MD5 values |
| IPS applies from clean base ROM | PASS | none | candidate IPS files are generated from clean base-to-patched byte diffs |
| release zip contains no ROM | UNKNOWN | PACKAGE_TEST_NOT_PART_OF_CANDIDATE_BUILD | validated separately by scripts/test_release_package_contents.py after packaging |
| regression boot smoke | PASS | none | smoke_summary_*.tsv files report lua_done for candidate boot tests |

## Development Soft Gate

- [x] Select one active string from one known screen/context.
- [x] Record ROM offset, PRG bank, bytes, and context.
- [x] Build a one-string candidate ROM/IPS.
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

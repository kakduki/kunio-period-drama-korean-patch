# Test Guide

The project uses a soft gate during development and a hard gate only for release approval.

## Required development checks

- Base identity: size, header, CRC32, MD5, SHA-1, and SHA-256 match the recorded Japanese base.
- Patch application: the output is a new file and has a deterministic hash.
- Runtime: the candidate boots and reaches the bounded test route.
- Text: at least one Korean label or dialogue string is read from the expected runtime source.
- Visual: native emulator evidence is required for release candidates and high-risk changes.

Use `tests/test-cases.csv` as the compact checklist. Results are `PASS`, `FAIL`, or `UNKNOWN`, with the reason recorded in `tests/known-issues.md` or the relevant `rom_analysis/` report.

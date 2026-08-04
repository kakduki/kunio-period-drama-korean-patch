# Changelog

## 2026-08-04

- Added the reproducible base-ROM identity and English-reference analysis documents.
- Added text, pointer, font, Korean-font, build, and test guides.
- Added translation glossary, style guide, script manifest, and known-issues ledger.
- Added safe reference application, binary diff, changed-region, string, pointer, and CHR analysis tools.
- Extended `build.py` to generate an IPS diff from the verified Japanese base to a candidate ROM.
- Kept release status `NOT_READY`; this is a development candidate pipeline, not a finished full translation.
- Pointed the default build at the tracked development IPS and added a clean-build hash regression test.
- Added an automated 10-record boss-dialogue target queue that preserves the natural-route UNKNOWN gate.
- Verified the full-pointer candidate can be regenerated from tracked translation/structure/font inputs; external output paths now produce portable reports.

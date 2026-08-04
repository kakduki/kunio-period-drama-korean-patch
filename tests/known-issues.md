# Known Issues

## Release blockers

- The full Japanese dialogue script is not yet normalized into a reviewed Korean translation manifest.
- The natural boss route is not yet demonstrated by a bounded automated route.
- The current merged candidate quarantines 57 pre-pointer overflow rows.
- One required glyph is still missing from the current merged candidate.
- Full-game native visual evidence is `UNKNOWN`.

## Interpretation

These are development findings, not reasons to stop producing a minimal candidate. A row can be promoted independently when its source, bank, pointer, width, glyph coverage, runtime read, and screen context are all proven.

## Pipeline Verification

The following development checks are now `PASS`: base identity, candidate IPS reproduction, external English-reference copy, structural extraction, binary diff, pointer scan, minimal font payload, CHR expansion audit, and external-output candidate insertion. These checks prove tooling and bounded artifacts; they do not promote the full candidate to release.

## Manifest Overlay Gate

The optional translation/script.csv overlay currently applies two pointer rows (182 and 185) and skips three rows with unknown ownership. The two-row build is reproducible, but native visual approval and the relocated full-candidate runtime route remain UNKNOWN.

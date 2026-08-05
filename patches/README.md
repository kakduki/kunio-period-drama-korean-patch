# Patch Artifacts

The IPS file in this directory is a development candidate generated from the
verified Japanese base. It is the only game-data artifact intended for a
future distribution package; original ROMs, English-applied ROMs, and
candidate ROMs remain local and are not committed.

## Current artifact

- File: `kunio_period_drama_korean_development.ips`
- Format: IPS
- Status: `NOT_READY`
- Target base: Japanese iNES ROM, 262,160 bytes
- Target base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Target base SHA-256: `54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a`

The patch is generated with `build.py --patch-output`. Apply it only to the
exact base identified above. It does not claim full-game Korean coverage.

Generated artifact identity:
- Size: 111600 bytes
- CRC32: 27D56940
- MD5: df8359ea51f9fd36de4c0d2117ad6a9c
- SHA-1: 7af669f79247243cc14cff1bce5d9c4be534722e
- SHA-256: aafef7806b705e189111be02e3b6f596a7c2adb1b939da2c5a4527f5bc055873
- Reproduced candidate MD5: 0a983c3d8494444935f000963f415253

## Four-row manifest candidate

`kunio_period_drama_korean_manifest_4row.ips` is a separate reproducible
development candidate generated from `translation/script.csv`. It contains
the four verified opening pointer rows (182-185) and is not a release patch.
Its build and runtime evidence are recorded in
`rom_analysis/manifest_4row_reaudit_2026-08-05.md`.

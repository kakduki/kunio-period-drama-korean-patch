# Broad Preview Candidate

This is an unverified manual-screen-test IPS. It is not the primary patch.

- Candidate: **v0.4.3 broad preview unverified**
- Base v0.4.2 MD5: `ea11dc002a1a7b07682ce00a754b1a61`
- Preview MD5: `f9a990581775963bc9d4875cada8ae10`
- Applied rows: **4**
- Skipped rows: **0**
- IPS records: **117**
- Local IPS: `output/kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified.ips`
- Local ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified.nes`

## Applied Rows

| ROM | expected text | Korean | original bytes | preview bytes | reason |
| --- | --- | --- | --- | --- | --- |
| `0x0440C` | かじや | 대장간 | `CA D0 E9` | `B5 93 AB` | non-overlapping broad-scan preview row |
| `0x048F4` | たつじ | 타츠지 | `07 09 03` | `89 98 A1` | non-overlapping broad-scan preview row |
| `0x052A5` | たつじ | 타츠지 | `82 84 7E` | `89 98 A1` | non-overlapping broad-scan preview row |
| `0x05BE5` | たつじ | 타츠지 | `97 99 93` | `89 98 A1` | non-overlapping broad-scan preview row |

## Rules

- Use this only for manual FCEUX screen comparison.
- Do not mark these rows as verified until the base-ROM CPU read and visible screen context gates pass.
- The tracked release remains v0.4.2 font-expanded unless the strict v0.4.3 proof builder approves rows.

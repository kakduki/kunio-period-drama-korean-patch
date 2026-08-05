# Unified candidate reproducibility recheck (2026-08-05)

## Inputs

The unified development candidate was rebuilt from the Japanese base and the two separate candidate inputs. No ROM was copied into the repository as a release artifact.

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Pointer-owner candidate MD5: `64b599ca6c502b635d216aebf5ce61b9`
- Non-pointer overlay candidate MD5: `5f348772bb6809b1df0e7f84ef2e7603`

Command:

```text
python scripts/compose_full_korean_unified_candidate.py --out-dir C:\tmp\kunio_unified_rebuild --report-json C:\tmp\kunio_unified_rebuild.json --report-markdown C:\tmp\kunio_unified_rebuild.md
```

## Result

- Existing candidate size: `475152` bytes.
- Rebuilt candidate size: `475152` bytes.
- Existing candidate MD5: `7fcf03377cff7536cf7b9a6db735d55e`.
- Rebuilt candidate MD5: `7fcf03377cff7536cf7b9a6db735d55e`.
- Full byte comparison: `True`.
- Composition summary: `5593` non-pointer overlay bytes applied; `1780` conflicts retained from the pointer owner.
- Existing unified IPS SHA-256: `1d103e503a4f8df8fa67e6fb1223b5262f786d37663d0965c39e805391f4c76d`.

## Gate

`PASS_REPRODUCIBLE_DEVELOPMENT_CANDIDATE`. This proves the composition pipeline is deterministic for the recorded inputs. It does not change the release gate: native visual coverage for all contexts and natural boss/event routing remain `UNKNOWN`, so the candidate remains `NOT_READY`.
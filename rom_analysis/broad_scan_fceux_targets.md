# Broad Scan FCEUX Targets

These targets watch original bytes for broad-scan promotion candidates.
They are for manual screen proof before promoting any new text into the v0.4.2 line.

- Source: `rom_analysis\broad_scan_patchability.json`
- Targets: **7**
- Preview rule: future patch preview uses v0.4.2 font bytes: base compact slots plus first 32 planned extra glyphs

Run after manually reaching the related screen:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_broad_scan_candidate_targets.lua --frames 900 --timeout 60 --final-output rom_analysis/fceux_broad_scan_candidates --clean-output --no-dump-hex --no-dump-bin
```

## Targets

| ROM | CPU range | confidence | source | korean | original bytes | future patch preview | new glyphs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `0x0440C` | `$83FC-$83FE` | medium | かじや | 대장간 | `CA D0 E9` | `0xB5 0x93 0xAB` | 대간 |
| `0x048F4` | `$88E4-$88E6` | medium | たつじ | 타츠지 | `07 09 03` | `0x89 0x98 0xA1` | 지 |
| `0x052A5` | `$9295-$9297` | medium | たつじ | 타츠지 | `82 84 7E` | `0x89 0x98 0xA1` | 지 |
| `0x05BE5` | `$9BD5-$9BD7` | medium | たつじ | 타츠지 | `97 99 93` | `0x89 0x98 0xA1` | 지 |
| `0x06294` | `$A284-$A287` | high | へいしち | 헤이시치 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | - |
| `0x0631B` | `$A30B-$A30E` | high | へいしち | 헤이시치 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | - |
| `0x06359` | `$A349-$A34C` | high | へいしち | 헤이시치 | `9D 82 8C 91` | `0x8D 0x8E 0x8F 0x90` | - |

## Promotion Rule

- A CPU read hit proves only that the record was read in that run.
- Promote to a v0.5 patch candidate only when the screen context also matches the intended label/dialogue.
- Under v0.4.2 these seven rows are font-ready, but visual/screen proof is still required before patching.

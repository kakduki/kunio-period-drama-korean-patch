# Test Guide

The project uses a soft gate during development and a hard gate only for release approval.

## Required development checks

- Base identity: size, header, CRC32, MD5, SHA-1, and SHA-256 match the recorded Japanese base.
- Patch application: the output is a new file and has a deterministic hash.
- Runtime: the candidate boots and reaches the bounded test route.
- Text: at least one Korean label or dialogue string is read from the expected runtime source.
- Visual: native emulator evidence is required for release candidates and high-risk changes.

Use `tests/test-cases.csv` as the compact checklist. Results are `PASS`, `FAIL`, or `UNKNOWN`, with the reason recorded in `tests/known-issues.md` or the relevant `rom_analysis/` report.

## Relocated Manifest Candidate Runtime Check

For a manifest candidate, generate source targets from its own pointer table
before launching FCEUX. This avoids reusing Japanese-base addresses:

```powershell
python scripts/generate_manifest_runtime_target.py --candidate $env:TEMP\kunio-manifest.nes --pointer-index 182 --pointer-index 185 --output $env:TEMP\kunio-manifest-targets.lua
python scripts/run_fceux_lua_analysis.py --rom $env:TEMP\kunio-manifest.nes --lua-script lua\kunio_opening_ptr_185_base_probe.lua --target-lua $env:TEMP\kunio-manifest-targets.lua --frames 1900 --timeout 60 --final-output $env:TEMP\kunio-manifest-runtime --clean-output --no-dump-hex --no-dump-bin
```

A zero-hit result is `UNKNOWN` until the candidate's relocated PRG/loader route
is separately proven; it is not evidence to extend free-running autoplay.

## Native Manifest Loader Trace

After building a manifest candidate, run the bounded loader trace and analyzer
to distinguish a route stall from a broken relocated pointer:

```powershell
python scripts/run_fceux_lua_analysis.py --rom $env:TEMP\kunio-manifest.nes --lua-script lua\kunio_manifest_loader_trace.lua --frames 1900 --timeout 60 --final-output $env:TEMP\kunio-manifest-loader-trace --clean-output --no-dump-hex --no-dump-bin
python scripts/analyze_manifest_loader_trace.py --trace $env:TEMP\kunio-manifest-loader-trace --json-out $env:TEMP\kunio-manifest-loader-trace.json --markdown-out $env:TEMP\kunio-manifest-loader-trace.md
```

`PASS` requires `lua_done`, the expected dialogue-ID progression, and exact
reads of the candidate-owned selected records. A target capture must separately
report `screenshot=true` and `target_match=true`; neither gate promotes the
remaining unverified rows or natural boss route.
# Real-Time Overlay Recheck

Date: 2026-08-06

## Result

The existing sidecar overlay was re-run against the verified Japanese base
ROM with a bounded 1,900-frame FCEUX session.

```text
python scripts/run_project_checks.py
python scripts/run_fceux_lua_analysis.py --rom "rom\\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\\kunio_translation_overlay.lua --target-lua lua\\kunio_translation_overlay_targets.lua --frames 1900 --timeout 120 --final-output C:\\tmp\\kunio_overlay_recheck_2026_08_06 --clean-output --no-dump-hex --no-dump-bin
python tools/realtime_translation_overlay.py --events C:\\tmp\\kunio_overlay_recheck_2026_08_06\\events.tsv --cache translation\\realtime_overlay.csv --once
```

Checks:

- Project checks: `PASS`
- FCEUX run: `lua_done` at frame `1900`
- Source-read events: `6`
- Reached IDs: `OPENING-182`, `OPENING-183`, `OPENING-184`, `OPENING-185`, `OPENING-194`
- Latest receiver result: `CACHED`
- ROM modification: none

## Interpretation

This is a usable immediate-play aid and a scene-evidence collector. It is not
full-screen OCR, automatic game progression, or release proof. Unknown source
events remain unreviewed and are not inserted into the ROM automatically.

The English IPS remains valuable for renderer, pointer, control-code, and font
layout analysis, but it does not provide Korean translations or a boss-route
warp. The native patch and the overlay should therefore remain parallel tracks:
overlay for immediate play and evidence collection, native ROM patch for the
offline final artifact.

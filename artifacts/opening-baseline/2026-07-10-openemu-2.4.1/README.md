# Japanese Opening Baseline — OpenEmu 2.4.1

## Result

A Japanese-reference **opening menu** baseline was captured from a live OpenEmu game window and repeated three times under the same rectangular window-capture procedure. The primary image and all three repeats are byte-identical.

- Runtime: OpenEmu 2.4.1 on Intel macOS 12.7.6
- ROM window title: `kunio`
- Captured window rectangle: `402,77,876,748` points
- PNG output: `1752 × 1496` pixels (Retina scale)
- Visual review: the live game screen shows Japanese menu text and `© 1991 TECHNOS JAPAN CORP.`; no OpenEmu import/onboarding/error dialog is present.

## Artifact inventory

| File | SHA-256 |
|---|---|
| `opening-baseline-primary.png` | `fec355884d83df7214dae1d257457107fc33033de0bc4f761aacb8d44e38049a` |
| `repeat-01.png` | `fec355884d83df7214dae1d257457107fc33033de0bc4f761aacb8d44e38049a` |
| `repeat-02.png` | `fec355884d83df7214dae1d257457107fc33033de0bc4f761aacb8d44e38049a` |
| `repeat-03.png` | `fec355884d83df7214dae1d257457107fc33033de0bc4f761aacb8d44e38049a` |

## Repeatability verdict

`PASS — exact PNG-byte match (3 / 3 repeat captures).`

The primary image is also byte-identical to every repeat. This verdict is limited to the captured opening-menu state, active window geometry, and the stated OpenEmu runtime.

## Reproduction

```bash
python3 scripts/capture_openemu_opening_baseline.py \
  --output-dir artifacts/opening-baseline/2026-07-10-openemu-2.4.1
```

The script activates the existing OpenEmu window titled `kunio`, captures the exact window rectangle once as the primary artifact and three times as repeats, then writes `repeatability.json`.

## Evidence boundary

This is visual baseline evidence only. It does **not** prove FCEUX Lua compatibility, emulator RAM/PPU/nametable values, translation-target context, or release-gate approval.

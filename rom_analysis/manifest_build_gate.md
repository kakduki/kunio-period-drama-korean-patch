# Translation Manifest Minimal Build Gate

Date: 2026-08-05

The manifest build was run from the verified Japanese base using
`translation/script.csv`. The build treats manifest rows as an explicit
allow-list; unselected rows remain on the original pointer/font path and are
not compiled into the relocated Korean record pool.

## Result

- `manifest_updates=1`
- `manifest_skipped=3` (`MENU-ITEMS`, `ITEMS-USE`, `ITEMS-REMOVE` have no verified pointer address)
- Candidate size: `368656` bytes
- Candidate MD5: `b5afc3e437238cc4e9186f2b19c56214`
- Candidate status: `NOT_READY`
- Generated IPS size: `107088` bytes
- Generated IPS MD5: `46b7fb8914b7ef31624db97e73635426`
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`

The selected row receives an isolated Korean font page and pointer assignment.
The candidate has not received natural-route or native-pixel visual approval;
those gates remain `UNKNOWN`.

## Regression Evidence

- `scripts/test_insert_text_manifest.py`: `PASS`
- `python -m py_compile tools/insert_text.py scripts/build_full_pointer_korean_candidate.py`: `PASS`
- The default IPS build remains independently reproducible at candidate MD5
  `0a983c3d8494444935f000963f415253`.
## Bounded FCEUX Check (2026-08-05)

The candidate was run with the correct watcher/target pairing:

```text
python scripts/run_fceux_lua_analysis.py --rom C:/tmp/kunio_manifest.nes --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_opening_ptr_182_183_16x16_p182_target.lua --frames 900 --timeout 90
```

- Emulator completion: `lua_done` at frame `900`
- Registered target bytes: `33`
- Source-read hits: `0`
- Boot/bounded process: `PASS`
- Opening pointer source-read: `UNKNOWN_ROUTE_NOT_REACHED`
- Release status: `NOT_READY`

The watcher intentionally does not inject the opening menu route, so zero hits
is route evidence rather than proof that the candidate text is broken. The
existing dedicated opening proof remains the authoritative visual/source-read
proof for the three-record component.

## Two-Row Manifest Recheck (2026-08-05)

The tracked manifest now contains two verified pointer rows: `OPENING-182` and
`OPENING-185`. From the exact Japanese base, `build.py --manifest` produced:

- `manifest_updates=2`
- `manifest_skipped=3` (`MENU-ITEMS`, `ITEMS-USE`, `ITEMS-REMOVE`)
- Candidate size: `368656` bytes
- Candidate MD5: `03c8abce53e019b39d0efad17c82fe98`
- Generated IPS size: `107106` bytes
- Generated IPS MD5: `06b51f4291dfb6ef933e779915e4f377`
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Development status: `NOT_READY`

The static validator reports both pointer rows as `static_status=PASS`, while
runtime/native visual approval remains a separate gate. The temporary build
outputs were written outside the repository under `C:\tmp`.

## Corrected Native Recheck (2026-08-05)

The first manifest candidate exposed a real loader defect: its page-table index
used `TAX/DEX` and corrupted the caller's X register, producing a repeated
`B6` dialogue-ID loop. The helper now uses `TAY/DEY` and preserves X without
exceeding the 64-byte cave.

The rebuilt candidate (`a5432d693a51e682bd23760a76e1c3ad`) passes the bounded
loader trace and the selected-row native visual captures. p182 is read at
`$9FB4` and captured at frame 712; p185 is read at `$9FCE` and captured at
frame 1661. Both report exact target matches. Full dialogue and natural event
routes remain separate `UNKNOWN` gates.
## Four-Row Native Recheck (2026-08-05)

The manifest now selects p182, p183, p184, and p185. The rebuilt candidate is
`b6ae36bb14ac1ba0836e7d02204d4b57` with IPS MD5
`88ae9e0bf1b2d12a9dacfe73d4573b41`. The generated pointer targets are
`$9FB4`, `$9FCE`, `$9FDC`, and `$9FE9`; the loader trace reads 64/64 selected
bytes and all four bounded visual captures report exact target matches. This
selected-row gate is `PASS`; full dialogue, dynamic contexts, and release gates
remain separate `UNKNOWN`/`NOT_READY` states.
## Current Eight-Row Promotion (2026-08-05)

The tracked main manifest has since been promoted to eight opening rows
p182-p189. The reproducible candidate is MD5
`e0b450a50083dc9dc67aee10af9d130d`; native source-read and lower-dialogue-band
PPU/pixel gates pass for all eight rows. This supersedes the earlier one-,
two-, and four-row milestone counts in this historical report. Broader game
contexts and release approval remain `NOT_READY`.
## Twelve-Row Promotion Gate (2026-08-05)

`p190-p193` are now included in the main development manifest after bounded native runtime evidence. The build applied 12 manifest rows and skipped 3 intentionally unresolved menu rows. This is a development promotion only; pixel screenshot, natural gameplay/event/boss, full 244-row regression, and release gates remain open.

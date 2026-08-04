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
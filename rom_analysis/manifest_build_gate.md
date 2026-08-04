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
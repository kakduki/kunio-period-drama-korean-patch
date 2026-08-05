# Items Candidate Visual Review (2026-08-06)

## Evidence

The screenshots were decoded from FCEUX captures with `scripts/convert_fceux_gd_to_png.py` where needed and reviewed as images.
- `rom_analysis\state_page_probe_raw\guard_items_base\main_menu_frame_001960_screen.png`: SHA-256 `6BA8C2892FEE924D624F92575989C1DEA44FE5B4E2E40EDF4846CB948D0866BB`
- `rom_analysis\state_page_probe_raw\development_candidate_items\main_menu_frame_001960_screen.png`: SHA-256 `6BA8C2892FEE924D624F92575989C1DEA44FE5B4E2E40EDF4846CB948D0866BB`
- `C:\tmp\items_clean_merged_1906.png`: SHA-256 `0A308E55B60FA3B43C10C05FA21C64BD65AA40A60410F9926EAA7CC5BA4AE09F`
## Findings

- The Japanese guard capture visibly shows the inventory-list screen, including the Japanese inventory header and bottom action labels.
- The older development candidate capture reaches the same inventory-list layout and is suitable as a route/isolation reference.
- The current integrated `items_clean_merged_runtime` evidence captures `main_menu_frame_001906_screen.gd`. Its converted PNG shows a shop/field scene with characters and shop structures, not the inventory-list screen.
- The integrated candidate queue and PPU byte checks are useful source/renderer evidence, but they do not prove that the Korean item label is visible in the intended inventory context.

## Gate Decision

| Gate | Result | Reason |
| --- | --- | --- |
| FCEUX screenshot decoding | PASS | GD capture converted to standard RGB PNG. |
| Japanese inventory route reference | PASS | Guard image visibly shows the inventory-list layout. |
| Integrated candidate inventory visual context | FAIL | Captured frame is a shop/field scene, not the inventory list. |
| Korean item-label visual proof | UNKNOWN | No reviewed candidate screenshot shows the intended Korean item label in the inventory list. |
| Candidate promotion/release | NOT_READY | Keep item-label bytes in development/quarantine scope. |

The next capture must preserve the proven inventory route and save a screenshot at its actual item-list frame, not only at the later frame 1906 summary capture.
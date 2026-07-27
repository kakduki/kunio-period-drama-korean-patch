# Korean Main Menu Candidate Smoke Test

Soft-gate status: **SOFT_GATE_PASS**
Release verdict: **UNKNOWN**

## Evidence

- Candidate MD5: `de688d4bf18760cc4fa0682fee5571df`.
- Menu capture completion: `lua_done`.
- Final MMC3 R1: `46`; expected `0x46`.
- Raster R1 clone writes: `517`.
- Screen evidence: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\rom_analysis\main_menu_korean_candidate_capture\main_menu_frame_001906_screen.png`.

## Checks

- `candidate_template_matches_declared_layout`: PASS
- `source_bank7_chr_pair_unchanged`: PASS
- `clone_chr_pair_changed`: PASS
- `lua_done`: PASS
- `captured_template_matches_candidate`: PASS
- `captured_mirror_matches_candidate`: PASS
- `final_mapper_r1_is_clone`: PASS
- `raster_trace_contains_clone_r1`: PASS
- `screen_capture_available`: PASS

## Limits

- This is one fixed menu context, not a broad screen-compatibility audit.
- The R1 raster split is shared outside this context; release approval remains UNKNOWN.
- Cursor motion and menu return need separate bounded screen captures.

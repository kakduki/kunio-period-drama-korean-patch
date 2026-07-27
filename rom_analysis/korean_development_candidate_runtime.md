# Korean Development Candidate Runtime

Status: **SOFT_GATE_PASS_COMBINED_CANDIDATE**
Release verdict: **UNKNOWN**

- Candidate MD5: `6474e2d857dbbcbf1ce8f1e5d8201c08`.
- The menu route, Items page-isolation route, and all three opening pointer routes use fixed frame caps and ended with `lua_done`.

## Checks

- `candidate_base_md5`: PASS
- `menu_lua_done`: PASS
- `menu_template_matches_candidate`: PASS
- `menu_clone_r1_active`: PASS
- `menu_clone_copied_from_original_source`: PASS
- `menu_screen_available`: PASS
- `items_lua_done`: PASS
- `items_screen_pixel_equal_to_base`: PASS
- `opening_lua_done`: PASS
- `opening_p182_target_match`: PASS
- `opening_p183_lua_done`: PASS
- `opening_p183_target_match`: PASS
- `opening_p184_lua_done`: PASS
- `opening_p184_target_match`: PASS

## Limits

- This is a development candidate for three opening records and the main-menu labels.
- Items page isolation passed, but Items Korean text itself is not translated in this candidate.
- Other dialogue records, combat progression, cursor lifecycle, and release-wide shared CHR contexts remain UNKNOWN.

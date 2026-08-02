# Clean Merged Candidate Runtime Audit

- Status: **SOFT_GATE_PASS_CLEAN_MERGED_CANDIDATE**.
- Release status: **NOT_READY**.
- Candidate MD5: `2fba4bae8c65c31a2ebd96c7ed0f7fc9`.
- Candidate size: `368656` bytes; appended CHR tail preserved: `True`.

## Ownership Safety

- Pointer core spans preserved: `{'renderer_hooks': True, 'pointer_table': True, 'pointer_records_and_loader': True}`.
- Candidate-vs-pointer changed bytes: `2433`; unexpected outside declared overlay ranges: `0`.
- Safe pre-pointer additions: `63`; existing 22-row high-code rows preserved: `22`.
- Quarantined by glyph-pool overflow: `57`; missing glyph: `1`.

## Runtime Gates

- Fixed-label runtime: `22/22` exact Korean owners; `lua_done`=True at frame `900`.
- Items action verifier: `PASS`.
- Items name/title/NONE byte gate: `PASS_BYTE_PROOF_VISUAL_UNKNOWN`; queue frames `{'name': 1737, 'title_suffix': 1737, 'none': 1737}`.
- Full-pointer input route: `lua_done`=True; screen changes `[302, 306, 310, 328, 655, 666]`; first dialogue route reached=True.
- Stage progression: `lua_done`=True at frame `7200`; unique screens `16`; combat frames `[915, 1049, 1139, 1229, 1319, 1444, 1651, 1866, 1956, 2046]`.

## Remaining Gates

- Native visual gate: **UNKNOWN_NATIVE_GDSCREENSHOT_TRANSPARENT**.
- Natural boss route: **UNKNOWN**.
- Release promotion: **NOT_READY**.

This candidate is the clean integration base for continued work. It keeps the English patch's full-pointer renderer and appended font pages, then applies only bounded non-pointer owner chains. It does not claim that every Korean wording has been Japanese-context reviewed or visually approved.

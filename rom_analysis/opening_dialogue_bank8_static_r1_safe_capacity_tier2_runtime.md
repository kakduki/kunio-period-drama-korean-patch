# Opening Bank 8 Static R1 Safe Capacity Tier-2 Runtime

Status: **SOFT_GATE_PASS_SAFE_STATIC_R1_CAPACITY_RUNTIME_AND_VISUAL**

- Candidate MD5: `7b7e4ff92c69cc256148a9c5b6fbdfde`.
- Mapper lifecycle: normal setup `R1=3E -> 46`; bounded run ended `lua_done`.
- Runtime source reads: `37/37`; emitted tile rows: `70`.
- Runtime font mapping audit: **PASS** for `67/67` emitted rows.
- Native screenshot: `opening_dialogue_bank8_static_r1_safe_capacity_tier2_capture/renderer_probe_frame_000883_screen.png`.
- Visual result: opening background, dialogue window, and expanded Korean-looking glyph output remain visible.

The candidate clones the actual original R1 `0x800`-byte runtime window into
the new R1 window, keeps the source Bank 7 window intact, and writes the
expanded glyph tiles only into the runtime Bank 8 window. This is a bounded
opening-context capacity result, not whole-game font approval.

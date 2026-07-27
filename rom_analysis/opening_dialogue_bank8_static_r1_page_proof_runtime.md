# Opening Bank 8 Static R1 Page Proof Runtime

Status: **FAIL_STATIC_R1_VISUAL_BACKGROUND**

- Candidate MD5: `7b41d2b1dcd2449d667520ff78c80161`.
- Mapper lifecycle: normal setup `R1=3E -> 46`; original fixed mapper routine preserved.
- Bounded FCEUX result: frame `883`, `lua_done`, `18/18` source reads.
- Emitted tile rows: `34`; runtime font mapping audit: `28/28` PASS.
- Native screenshot: `opening_dialogue_bank8_static_r1_page_proof_capture/renderer_probe_frame_000883_screen.png`.

The runtime mapping audit passes `28/28`, but the native screenshot is a
dialogue-only black frame. The candidate is not a visual page-lifecycle pass.
The corrected R1-window candidate is recorded separately in
`opening_dialogue_bank8_static_r1_safe_capacity_tier2_runtime.md`.

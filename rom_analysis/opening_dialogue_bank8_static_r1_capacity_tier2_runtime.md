# Opening Bank 8 Static R1 Tier-2 Runtime

Status: **FAIL**

- Candidate MD5: `4246230abe23bbce7abae9affdf5bcdb`.
- Mapper lifecycle: normal setup `R1=3E -> 46`; bounded run ended `lua_done`.
- Runtime source reads: `37/37`; emitted tile rows: `70`.
- Runtime font mapping audit: **FAIL** for `67` rows because the candidate
  declarations remain at Bank 7 while runtime emission is at Bank 8.
- Native screenshot: `opening_dialogue_bank8_static_r1_capacity_tier2_capture/renderer_probe_frame_000883_screen.png`.
- Visual result: dialogue text is visible, but the opening background is lost;
  the candidate is not promoted.

The direct Bank-7 tier-2 capacity result remains valid as a source-slot probe.
This cloned-page variant does not establish a safe allocation for `C0-C7`.

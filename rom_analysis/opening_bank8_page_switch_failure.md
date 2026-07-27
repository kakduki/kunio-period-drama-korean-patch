# Opening Bank 8 Page-Switch Results

Status: FAIL, excluded from Korean translation candidates

## Candidate A: Transient Page Write

- Build: `opening_dialogue_bank8_page_switch_proof`
- Bounded route: `lua_done`, frame 883
- Target record: PASS, 18/18 source reads matched pointer 182
- Final mapper snapshot: MMC3 control `0x07`, R0/R1 `0x3C/0x3E`
- Expected cloned page mapping: R0/R1 `0x40/0x42`
- Result: FAIL

The renderer-side helper did write the clone-page values. The mapper trace
shows `0x40/0x42` briefly, followed by the game's normal `0x3C/0x3E` update
in the same frame. The final frame therefore maps physical CHR Bank 7, not
the cloned Bank 8 page. This does not prove a readable Bank 8 dialogue page.

Evidence:

- `rom_analysis/opening_dialogue_bank8_page_switch_proof_capture/analysis.md`
- `rom_analysis/opening_mapper_trace_bank8_page_switch_candidate/analysis.md`
- `rom_analysis/opening_dialogue_renderer_probe_bank8_page_switch_candidate/analysis.md`

## Candidate B: Persistent Mapper Hook

- Build: `opening_dialogue_bank8_persistent_page_proof`
- Bounded route: `lua_done`, frame 883
- Target record: FAIL, 0/37 source reads matched
- Screen capture: black screen at the capture frame
- Result: FAIL

The fixed mapper code at CPU `FEDD` was redirected to helper code at CPU
`BFEB`. That helper lives in the Bank 1 window, whose PRG bank is not fixed
when the mapper routine executes. The route continued far enough to emit a
capture, but no longer mapped pointer 182 correctly. The result rules out
fixed-bank-to-Bank-1 jumps as a page-persistence implementation technique.

Evidence:

- `rom_analysis/opening_dialogue_bank8_persistent_page_proof_capture/analysis.md`
- `rom_analysis/opening_dialogue_bank8_persistent_page_proof_capture/opening_dialogue_frame_000883_screen.png`

## Next Gate

Do not build another dynamic-page dialogue candidate until a harmless helper
can execute from a verified fixed PRG location throughout the relevant mapper
updates. That gate is independent of translation text and of gameplay route
automation.

## Static R1 Follow-Up

The normal mapper setup at ROM `0x1EE57` writes the opening pair `R0=3C,
R1=3E`. A bounded candidate changing only the immediate `3E -> 46` kept the
original fixed mapper routine and normal `STA $FC` lifecycle intact.

### Small Page Candidate

- Build: `opening_dialogue_bank8_static_r1_page_proof`
- Result: **SOFT_GATE_PASS**
- Candidate MD5: `7b41d2b1dcd2449d667520ff78c80161`
- Runtime: frame `883`, `lua_done`, `18/18` source reads, `34` emitted tile rows.
- Mapper state: `R0=3C, R1=46`; runtime font mapping audit: **PASS** (`28/28`).
- Native screenshot: `rom_analysis/opening_dialogue_bank8_static_r1_page_proof_capture/renderer_probe_frame_000883_screen.png`.

This is the first page-lifecycle candidate that preserves the opening scene
while displaying the bounded Korean sample. It is not yet a whole-game page
allocation.

### Tier-2 Page Candidate

- Build: `opening_dialogue_bank8_static_r1_capacity_tier2`
- Result: **FAIL** for the static-page gate.
- Candidate MD5: `4246230abe23bbce7abae9affdf5bcdb`.
- Runtime: frame `883`, `lua_done`, `37/37` source reads, `70` emitted tile rows,
  and `R1=46`.
- Runtime mapping audit: **FAIL** because the declared Bank-7 font targets
  do not match the Bank-8 runtime slots; the native capture also loses the
  opening background and shows only the dialogue text.
- Native screenshot: `rom_analysis/opening_dialogue_bank8_static_r1_capacity_tier2_capture/renderer_probe_frame_000883_screen.png`.

The direct Bank-7 tier-2 capacity proof remains useful for source-slot
capacity. Its `C0-C7` expansion is not approved for a static cloned page until
the page-specific slot ownership and visual context are re-established.

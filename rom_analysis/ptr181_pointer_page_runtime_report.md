# PTR-181 Pointer Page Runtime Report

Status: **PASS_WITH_RESTORE_UNKNOWN**

## Pass

- The candidate booted in FCEUX and completed the bounded 450-frame route.
- PTR-181 (`$B188`) was read and rendered.
- RAM at capture: `$07FD=00`, `$07FE=B6`, `$07FF=04`, `$51=13`.
- MMC3 capture: `R0=$3C`, `R1=$86`.
- The Korean 8x16 line is visible and the field background remains intact.
- This proves the runtime chain `dialogue ID -> page table -> $07FF -> R1`.

## Unknown

The focused 1200-frame route reached the dialogue at frame 330 but its scripted
A/B inputs did not dismiss that screen. It therefore could not observe the
normal-state transition to `$07FF=00`, `R1=$3E`.

Failure class: `INPUT_ROUTE_DID_NOT_DISMISS_DIALOGUE`.

No longer autoplay run is justified. Restoration remains a release/high-risk
gate; candidate production can continue under the development soft gate.

## Evidence

- `ptr181_pointer_page_runtime/summary.tsv`
- `ptr181_pointer_page_runtime/mapper_state.tsv`
- `ptr181_pointer_page_runtime/frame_000392_cpu_ram.bin`
- `ptr181_pointer_page_runtime/frame_000392_screen.png`
- `ptr181_page_restore_probe/summary.tsv`

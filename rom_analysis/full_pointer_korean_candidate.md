# Full Pointer Korean Candidate

Status: **WHOLE_SCRIPT_RUNTIME_PASS_PTR181**

- English reference role: pointer ownership and non-letter control-byte order.
- Korean replacement scope: English `0x81-0x9A`/space runs only.
- Compiled records: `247`; bytes: `3894`.
- Record range: `0x05FC4` to `0x06EFA`.
- Gap before loader: `262` bytes.
- Korean CHR pages: `49`; CHR banks: `16 -> 29`.
- Static display-width audit: **PASS**, maximum `24/24` cells; two warnings
  above 20 cells and zero failures.
- Excluded non-dialogue records retain their Japanese bytes.
- This is a soft-gate whole-script candidate; translation review and broad runtime coverage remain open.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `2f706986e429a1acba9238d551f640d0`.

## Runtime

- FCEUX boot and bounded opening-to-field route: **PASS**
- Relocated PTR-181 address: `$AAF4`
- Dialogue ID: `$B6`
- Page state: `$07FF=2C` (page 43 + 1)
- Computed and observed MMC3 R1: `$D6`
- Korean line visible with the field background preserved: **PASS**

This proves one representative record through the complete whole-script path:
relocated pointer, preserved controls, optimized page table, appended CHR page,
generic renderer, and mapper selection. Broad scene coverage remains a release
gate rather than a development build gate.

The complete per-record segment list is in
`rom_analysis/full_pointer_korean_layout_audit.csv`.

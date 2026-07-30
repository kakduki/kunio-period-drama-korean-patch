# Full Pointer Korean Runtime Report

Status: **PASS_PTR181**

## Static Coverage

- Pointer rows: 248
- Korean dialogue rows: 244
- Excluded non-dialogue rows retained from Japanese: 4
- Nonempty packed records: 247
- Packed bytes: 3,894
- Packed range: ROM `0x05FC4-0x06EF9`
- Loader starts at ROM `0x07000`; remaining gap: 262 bytes
- Optimized Korean font pages: 49
- CHR expansion: 16 to 29 banks
- IPS round trip: PASS
- Every active record preserves the English reference's non-letter control
  skeleton.

## Runtime Coverage

The full candidate booted and reached relocated PTR-181 at `$AAF4` in the
existing bounded 450-frame route.

- `$07FE=B6`: runtime dialogue ID
- `$07FF=2C`: optimized page 43 encoded as page + 1
- `$07FD=00`: renderer temporary state cleared
- `$51=13`: target dialogue context
- MMC3 `R0/R1=$3C/$D6`
- Screenshot: Korean text visible; field background preserved

This is a development soft-gate pass for the whole-script build pipeline.
It is not a release-wide visual proof of all 244 translated records.

## Evidence

- `full_pointer_korean_ptr181_runtime/summary.tsv`
- `full_pointer_korean_ptr181_runtime/mapper_state.tsv`
- `full_pointer_korean_ptr181_runtime/frame_000392_cpu_ram.bin`
- `full_pointer_korean_ptr181_runtime/frame_000392_screen.png`

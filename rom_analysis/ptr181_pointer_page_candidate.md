# PTR-181 Pointer Page Candidate

Status: **CANDIDATE_RUNTIME_PASS_RESTORE_UNKNOWN**

- Dialogue loader hook: `$9137`.
- Runtime ID: `$B6`; catalog index: `181`.
- Development page state: `4`; computed MMC3 R1: `$86`.
- Renderer activation and CHR selection now depend on `$07FF`, not a hardcoded record pointer.
- The temporary loader/table region overlaps original Japanese records and is valid only for this bounded development candidate.
- The common loader starts at ROM `0x07000`; the whole-script compiler packs records before it.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `e96f33023190b1eeeaf8392a09d29e63`.
- Changed spans: `35`.

## Runtime

- Boot and bounded route: **PASS**
- PTR-181 source observed: **PASS**
- Dialogue ID state: `$07FE=B6`
- Page state: `$07FF=04`
- Mapper state at frame 392: `R0/R1=$3C/$86`
- Korean text visible with field background preserved: **PASS**
- Dismissal/restore: **UNKNOWN(INPUT_ROUTE_DID_NOT_DISMISS_DIALOGUE)**

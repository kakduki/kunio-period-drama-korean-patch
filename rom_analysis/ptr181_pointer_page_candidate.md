# PTR-181 Pointer Page Candidate

Status: **CANDIDATE_RUNTIME_PASS_RESTORE_UNKNOWN**

- Dialogue loader hook: `$9137`.
- Runtime ID: `$B6`; catalog index: `181`.
- Development page state: `4`; computed MMC3 R1: `$86`.
- Renderer activation and CHR selection now depend on `$07FF`, not a hardcoded record pointer.
- The temporary loader/table region overlaps original Japanese records and is valid only for this bounded development candidate.
- The final compiler must first relocate the complete Korean stream ending at ROM `0x06F88`.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`.
- Candidate MD5: `d4542dc5dd87f81264443c5a00ee3ba4`.
- Changed spans: `32`.

## Runtime

- Boot and bounded route: **PASS**
- PTR-181 source observed: **PASS**
- Dialogue ID state: `$07FE=B6`
- Page state: `$07FF=04`
- Mapper state at frame 392: `R0/R1=$3C/$86`
- Korean text visible with field background preserved: **PASS**
- Marker temporary state after rendering: `$07FD=00`
- Dismissal/restore: **UNKNOWN**

The focused 1200-frame dismissal route reached the target but did not close the
dialogue screen, so it could not observe `$07FF=00` and `R1=$3E`. This is
classified as `INPUT_ROUTE_DID_NOT_DISMISS_DIALOGUE`, not a mapper failure.

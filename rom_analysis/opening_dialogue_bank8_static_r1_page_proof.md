# Opening Bank 8 Static R1 Page Proof

Status: CANDIDATE_BUILT_PENDING_STATIC_R1_PROOF

- Base MD5: 0d406a85285b4de8468f0dab6aad5fe5
- Normal mapper setup: ROM `0x1EE57` / CPU `$EE47`
- R1 replacement: `3E -> 46`
- Candidate MD5: 7b41d2b1dcd2449d667520ff78c80161

The candidate keeps the original fixed mapper routine and changes
one normal setup value. The renderer-side transient page write is
disabled so the runtime result tests only the static R1 lifecycle.

# PTR-181 Dynamic Bank 8 Page Probe

Status: CANDIDATE_BUILT_PENDING_PTR181_DYNAMIC_RUNTIME_PROOF

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Pointer: `181` / CPU `$B188` / ROM `0x07198`
- Page switch: renderer entry only, R0/R1 `40/42`; normal mapper setup is untouched
- Candidate MD5: `a0889693feb741c6375eb22bc288d7c7`
- Declared changed spans: `101`

This is a renderer/font ownership probe. The text is deliberately a
glyph-coverage test and is not release translation prose.

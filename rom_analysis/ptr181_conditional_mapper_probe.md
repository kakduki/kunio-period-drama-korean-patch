# PTR-181 Conditional Mapper Probe

Status: **CANDIDATE_BUILT_PENDING_RUNTIME_PROOF**

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `b5f326deabbbdf791d775e9e9b5ad7c0`
- Mapper policy: the PTR-181 scene flag with `$51=13` selects `R0/R1=3C/46`; all other contexts select original `3C/3E`.
- The original fixed-bank wrapper still saves and restores `$0502/$0503`.

This is a bounded renderer/page-lifecycle candidate, not release prose.

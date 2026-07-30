# PTR-181 Expanded CHR Probe

Status: **CANDIDATE_BUILT_PENDING_EXPANDED_CHR_RUNTIME_PROOF**

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `390c18e7522e051745942a62098659d4`
- CHR banks: `16 -> 17` (one appended 8 KiB bank)
- Korean page: appended CHR Bank 16, MMC3 `R1=86`
- Existing CHR banks: byte-identical to the base ROM

This probe verifies scalable CHR expansion before multiple Korean pages
are compiled. It is not a release candidate.

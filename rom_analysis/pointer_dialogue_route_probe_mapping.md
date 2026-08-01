# Pointer Dialogue Route Mapping Diagnosis

- Candidate: full Korean development candidate.
- Probe: bounded 5,000-frame route watching relocated pointer-record CPU addresses.
- Expected target addresses: CPU 9FD6-9FE0 and 9FE1-9FF5.
- Result: UNKNOWN, target_not_seen.
- Watcher reads: 56 total by frame 5000.
- First repeated read context: frame 3165, target 9FE1.
- Observed bytes at 9FE1-9FF5: F3 85 60 01 00 00 01 00 00 00 01 00 90 09 20 17 86 20 6F 89 20.
- Expected Korean pointer-3 bytes: F0 BB 84 00 89 95 8C 00 85 99 86 CC F8 C0 B6 8A 8C 9A 98 CA FF.
- Screen fingerprint stabilized at 8507662:16320 during the watched phase.
- Failure class: ADDRESS_MAPPING_MISMATCH.
- Interpretation: the physical Bank-1 pointer relocation was treated as a fixed CPU address while the runtime mapper exposed another bank at that address. The route did not prove pointer 2 or 3 visibility.
- Action: do not extend the route blindly. A mapper-aware runtime pointer source or a bounded save-state/boss route is required before promoting these records.
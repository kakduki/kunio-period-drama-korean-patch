# Pointer Dialogue Batch Runtime

Status: **SOFT_GATE_BOOT_PASS_BOSS_TARGET_UNKNOWN**

- Candidate MD5: `863c62ba178973ee1a96cc7971512149`.
- Boot regression: **PASS** at frame `1095`.
- Pointer target watchers registered: `63`.
- Target probe: **UNKNOWN**; frame `1200`; reason `target_not_seen`.
- Extended route probe: **UNKNOWN**; frame `5000`; reason `target_not_seen`; phase `3`; reads `266`.

Reason: The extended route entered phase 3 and produced read activity, but the screen fingerprint stabilized and pointer 2/3 never matched.

The target probe is bounded and does not continue into free-form combat.
A target-not-seen result is not evidence that the candidate text is wrong;
it only classifies the current route as insufficient for pointer 2/3.

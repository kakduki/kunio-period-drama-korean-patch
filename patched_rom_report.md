# Patched ROM Report

Status: **PROOF_CANDIDATE_VISUALLY_VERIFIED_TWO_OPENING_CONTEXTS**

- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM MD5: `d1bd6e285c818ed60890282d8704f80a`
- English reference IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`
- Pointer 182: `0x05F40` -> `0x071B6` / `$B1A6`, 33 bytes.
- Pointer 183: `0x05F42` -> `0x071D7` / `$B1C7`, 25 bytes; pointer 184 remains `$B1E0`.
- Candidate Korean records: `쿠니오: 서둘러! 분조두목 위험!` and `오코토: 쿠니오! 기다렸어!`.
- Changed spans: 126; escaped bytes: 0.
- Font profile: `readable` (14 px, BOX resampling, threshold 145).
- Runtime evidence: pointer 182 passed 33/33 reads at frame 883; pointer 183 passed 25/25 reads at frame 1095; both bounded Lua runs ended with `lua_done`.
- Native visual review: PASS for both screens.

The generated ROM and IPS remain local/ignored. This report records only the
reproducible inputs, scoped result, and verification evidence. It is not a
release-ready full translation.

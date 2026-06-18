# Release Gate Checklist

Hard gates apply only to release candidates, not to soft-gated development builds.

## Development Soft Gate

- [x] Select one active string from one known screen/context.
- [x] Record ROM offset, PRG bank, bytes, and context.
- [x] Build a one-string candidate ROM/IPS.
- [x] Run emulator boot smoke test.
- [x] Classify result as PASS/FAIL/UNKNOWN.

## Release Hard Gate

- [ ] Manual visual proof for every release-included string.
- [ ] No known false-positive or ambiguous byte ranges patched.
- [ ] Base ROM hash and patched ROM hash documented.
- [ ] IPS applies cleanly from a clean base ROM.
- [ ] No `.nes` files in release zip.
- [ ] Regression smoke test passes on the release candidate.

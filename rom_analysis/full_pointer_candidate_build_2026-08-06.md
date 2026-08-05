# Full Pointer Korean Candidate Build (2026-08-06)

Status: `WHOLE_SCRIPT_CANDIDATE_BUILT_RUNTIME_UNKNOWN`

This is a development candidate generated from the verified Japanese base and the
tracked full pointer translation manifest. It is not a release patch.

## Build facts

- Source ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Source ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Source ROM SHA-256: `54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a`
- Reviewed manifest rows: `244/244`
- Record end: `0x06EB0`
- Font pages allocated: `50`
- Candidate ROM size: `368656`
- Candidate ROM MD5: `165ede9d7cf426a3f8aa841af4268a44`
- Candidate ROM SHA-256: `D2955399B7EBEF39A325BEA79BEBE04815E0337100E51FCA3B7440B50259D4BA`
- IPS size: `111600`
- IPS SHA-256: `6045C979B784D0A795E930F8A424406EE71E37A57C779C8A19852E054C07FC77`

## Verification

- Full pointer structural audit: `PASS`, `244/244`
- Korean layout audit: `PASS`, maximum encoded width `20`
- IPS application from exact base: `PASS`
- Native runtime evidence: `PARTIAL`
  - Rows `p182-p195` have bounded source-read and lower-dialogue-band PPU evidence.
  - Gameplay entry and interaction screens were reached in the progression probe.
  - Combat, boss transitions, save/load, ending, and all later rows are not yet release-gated.
  - Later target reads without a complete dialogue-band render are retained as `UNKNOWN` or false positives.

The candidate is useful for continuing runtime investigation and for testing the
full build pipeline. Do not distribute it as a completed Korean patch.
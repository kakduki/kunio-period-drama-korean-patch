# Patched ROM Report

## Candidate

- Build id: `softgate-0562f-tatsuichi`
- Build status: `PASS`
- Base ROM: `rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate ROM: `output\kunio_period_drama_softgate_0562f_tatsuichi.nes`
- Candidate IPS: `output\kunio_period_drama_softgate_0562f_tatsuichi.ips`
- Candidate MD5: `8bbe0f8b3ce78f37c9c77801993b72a4`

## Selected String

- Source: `たついち` / Tatsuichi
- Korean test string: `타츠이치`
- ROM offset: `0x0562F`
- PRG bank: `1`
- PRG offset: `0x0561F`
- Screen/context: `fceux_input_explorer_v042 frame 883 dialogue screen`
- Old bytes: `90 92 82 91`
- New bytes: `89 98 8E 90`

## Classification

- Patch classification: `PASS` when bytes match and candidate files are written.
- Boot smoke classification: `PASS`
- Visual classification: `UNKNOWN` until the exact string is visually confirmed on a release/high-risk pass.
- Failure class: `none`
- Failure reason: `none`

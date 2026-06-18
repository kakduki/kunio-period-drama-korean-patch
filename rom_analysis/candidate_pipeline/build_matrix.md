# Build Matrix

Development builds use a soft gate. Release approval uses the separate hard gate checklist.

| build id | scope | source screen/context | ROM offset | PRG bank | patch type | build | boot smoke | visual proof | decision |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| `softgate-0562f-tatsuichi` | one string | `fceux_input_explorer_v042 frame 883 dialogue screen` | `0x0562F` | 1 | equal-length PRG bytes + existing font expansion | PASS | PASS | soft gate only | candidate ROM produced |

## Notes

- Source string: `たついち` / `타츠이치` / Tatsuichi
- Source screenshot: `rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen.png`
- This matrix intentionally does not require manual visual proof for development candidates.

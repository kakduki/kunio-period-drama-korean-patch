# Tatsuji Clean Probe Runtime

- Candidate: `output/tatsuji_clean_probe/kunio_period_drama_korean_tatsuji_probe.nes`
- Candidate MD5: `38e0d4bc160006e68669520bfef92d4c`
- Route: bounded stage progression, 1200 frames
- Script completion: `PASS` (`lua_done` at frame 1200)
- Screen progression: `PASS` (9 unique fingerprints; combat captures reached)
- Capture pixel check: `PASS` (256x240, 5 colors, 4193 non-black pixels)
- Tatsuji boss/name screen: `UNKNOWN`; the bounded route did not reach the owner context
- Release status: `NOT_READY`

The ROM and the three equal-length Tatsuji owners are structurally valid for the
bounded smoke route. The name remains a soft-gate probe until one capture shows
the intended boss/name screen and the rendered Korean glyphs.

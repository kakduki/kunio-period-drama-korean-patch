# Full Pointer Rebuild Recheck

This report records a clean rebuild of the full pointer candidate from the
verified Japanese base. The candidate remains a development artifact; this
report does not promote natural event or boss-route coverage to release PASS.

## Static Rebuild

- Base ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Candidate size: `368656` bytes
- Candidate MD5: `165ede9d7cf426a3f8aa841af4268a44`
- Candidate IPS MD5: `2c66e0dd6d60248a321e111b85639d43`
- IPS re-application: `PASS` (re-applied bytes equal the rebuilt candidate)
- Layout audit: `PASS`, 244 active rows, maximum segment 20/24 cells
- Translation structure audit: `PASS`, 244 reviewed active rows, 4 excluded rows
- Dynamic control contexts: 47 flagged for later screen-specific review

## Bounded FCEUX Samples

The same bounded `lua/kunio_ptr181_renderer_probe.lua` was run against the
rebuilt candidate with the pointer loader forced to the selected record.

| pointer | target CPU | forced ID | source reads | capture | result |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | `$9FB4` | `01` | 2 | `lua_done` at frame 392 | `PASS_SAMPLE` |
| 188 | `$AB35` | `BD` | 84 | `lua_done` at frame 392 | `PASS_SAMPLE` |
| 243 | `$AE45` | `F4` | 2 | `lua_done` at frame 392 | `PASS_SAMPLE` |

These are forced-render samples. They verify that the rebuilt candidate boots,
accepts the relocated pointer/page path, and produces bounded captures. They do
not prove natural combat clear, boss spawn, or event ordering. The release gate
therefore remains `NOT_READY`.
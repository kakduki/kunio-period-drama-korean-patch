# Padding Experiment Matrix

This matrix tracks shortened PRG replacement experiments. These are not release candidates.

- Target: `ROM+0x071A4 ちから / Chikara -> 힘`
- Build artifacts: `PASS`
- CPU active-byte evidence: `PASS`
- PPU exact VRAM evidence: `UNKNOWN`
- Visual status: `UNKNOWN`
- Current font MD5: `af14a5b03d3b6b8631a1bed90cf4295e`

| experiment set | strategy | patched bytes | build | CPU active | active matches | PPU exact | VRAM matches | baseline | decision |
| --- | --- | --- | --- | --- | ---: | --- | ---: | --- | --- |
| `legacy-v02-font-base` | `pad_00` | `87 00 00` | PASS | PASS | 11 | UNKNOWN | 0 | STALE_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `legacy-v02-font-base` | `pad_7a` | `87 7A 7A` | PASS | PASS | 11 | UNKNOWN | 0 | STALE_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `legacy-v02-font-base` | `pad_ff` | `87 FF FF` | PASS | PASS | 4 | UNKNOWN | 0 | STALE_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `legacy-v02-font-base` | `pad_f8f9` | `87 F8 F9` | PASS | PASS | 9 | UNKNOWN | 0 | STALE_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `legacy-v02-font-base` | `preserve_tail` | `87 88 AA` | PASS | PASS | 11 | UNKNOWN | 0 | STALE_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `v05-current-font-base` | `pad_00` | `87 00 00` | PASS | PASS | 11 | UNKNOWN | 0 | CURRENT_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `v05-current-font-base` | `pad_7a` | `87 7A 7A` | PASS | PASS | 11 | UNKNOWN | 0 | CURRENT_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `v05-current-font-base` | `pad_ff` | `87 FF FF` | PASS | PASS | 4 | UNKNOWN | 0 | CURRENT_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `v05-current-font-base` | `pad_f8f9` | `87 F8 F9` | PASS | PASS | 9 | UNKNOWN | 0 | CURRENT_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |
| `v05-current-font-base` | `preserve_tail` | `87 88 AA` | PASS | PASS | 11 | UNKNOWN | 0 | CURRENT_FONT_BASE | UNKNOWN_VISUAL_PADDING_RULE |

## Interpretation

- `PASS` CPU active-byte evidence means the patched byte sequence was loaded on the known FCEUX route.
- `UNKNOWN` PPU/visual evidence means no padding strategy is safe to promote into the normal dev candidate yet.
- `STALE_FONT_BASE` means the experiment ROMs were built on an older font-expanded base and should be regenerated before another visual pass.

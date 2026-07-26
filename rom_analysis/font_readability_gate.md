# Korean Dialogue Font Readability Gate

Status: **PASS_FOR_ONE_RECORD_PAIRED_16X16_PROOF**

This is a development gate, not release approval. It deliberately separates a
working glyph path from a complete Korean translation and prevents the project
from returning to unbounded emulator autoplay.

## Compared Candidates

| candidate | native scene | runtime result | readability result | decision |
| --- | --- | --- | --- | --- |
| 8x8 raster baseline | opening dialogue, frame 883 | target record read and display pass | FAIL: syllable shapes are too compressed to review reliably | retain only as a structural baseline |
| 8x16 vertical-pair proof | same scene and frame | bounded boot, target read, and screen capture pass | FAIL at the intended Korean-quality bar: shapes are still too narrow to scale safely | retain as the technical building block |
| paired 8x16 cells (16x16 Korean) | same scene and frame | bounded boot, 37/37 target reads, and screen capture pass | PASS for this eight-glyph renderer/font proof: syllables, speaker mark, spaces, and punctuation are distinguishable without collisions | use as the provisional dialogue-font direction |

The 16x16 candidate does not add a new VRAM queue. It places two already-proven
vertical 8x16 cells side by side, so one Korean syllable has four 8x8 CHR tiles.
That keeps the runtime change bounded to the existing target-record gate.

## Evidence

- 8x8 baseline crop: `rom_analysis/opening_dialogue_proof_capture/opening_dialogue_frame_000883_dialogue_crop.png`
- 8x16 comparison crop: `rom_analysis/opening_dialogue_8x16_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- 16x16 full native screen: `rom_analysis/opening_dialogue_16x16_proof_capture/opening_dialogue_frame_000883_screen.png`
- 16x16 enlarged dialogue crop: `rom_analysis/opening_dialogue_16x16_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- 16x16 bounded smoke report: `rom_analysis/opening_dialogue_16x16_proof_capture/analysis.md`
- 16x16 runtime record evidence: `rom_analysis/opening_dialogue_16x16_proof_capture/opening_target_record.tsv`

The 16x16 bounded run ended with `lua_done` at frame 883. It registered 37
target-record reads, and the captured runtime bytes exactly matched the paired
candidate record. The runner stopped after that capture and never entered free
gameplay.

## Scope Limit

The pass covers only pointer-table entry 182 and the proof wording
`쿠니마사: 어서! 분조!`. That wording uses eight unique Korean syllables and
16 source slots. It was intentionally compact to prove the renderer and font;
it is not the final release translation for the record.

The current safe source pool has 17 one-cell codes (`0x81-0x89`,
`0x8C-0x93`), while a 16x16 syllable consumes two of them. Therefore it proves
only eight full syllables plus one spare code. It does not authorise bulk
translation, untested CHR slots, pointer relocation, menus, or event dialogue.

## Next Gate

1. Establish a release-capable dialogue glyph-capacity strategy: additional
   verified slots, scene-local CHR paging, or another renderer-owned path.
2. Add width-aware paired-cell encoding that preserves explicit line breaks,
   waits, speaker markers, and terminators.
3. Encode a full, context-checked opening record only after it fits the proven
   capacity strategy, then capture that exact scene with the same bounded route.

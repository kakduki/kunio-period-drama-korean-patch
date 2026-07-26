# Korean Dialogue Font Readability Gate

Status: **PASS_FOR_ONE_RECORD_8X16_PROOF**

This is a development gate, not a release approval. It records the decision
that lets the project begin a small, controlled script batch without returning
to blind FCEUX autoplay.

## Compared Candidates

| candidate | native scene | runtime result | readability result | decision |
| --- | --- | --- | --- | --- |
| 8x8 raster baseline | opening dialogue, frame 883 | target record read and display pass | FAIL for release-quality work: syllable shapes are too compressed to review reliably | retain only as a structural baseline |
| 8x16 vertical-pair proof | same scene and frame | bounded boot, target read, and screen capture pass | PASS for this 17-glyph proof: syllables, speaker mark, spaces, and punctuation are distinguishable with no tile collisions | use as the provisional dialogue renderer path |

The earlier 8x8 smoke report marked the scene as visually present. This stricter
gate answers a different question: whether the text is clear enough to scale
translation work. The answer for the 8x8 baseline is no.

## Evidence

- 8x8 baseline crop: `rom_analysis/opening_dialogue_proof_capture/opening_dialogue_frame_000883_dialogue_crop.png`
- 8x16 native crop: `rom_analysis/opening_dialogue_8x16_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box.png`
- 8x16 enlarged review crop: `rom_analysis/opening_dialogue_8x16_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- 8x16 bounded smoke report: `rom_analysis/opening_dialogue_8x16_proof_capture/analysis.md`
- Runtime record evidence: `rom_analysis/opening_dialogue_8x16_proof_capture/opening_target_record.tsv`

The bounded run ended with `lua_done` at frame 883. It registered 37 target
record reads, and the captured runtime bytes exactly matched the candidate
record. The runner stops after the capture and does not enter free gameplay.

## Scope Limit

The passing proof covers only pointer-table entry 182 and the glyph codes
`0x81-0x89`, `0x8C-0x93`. It does **not** prove that every Korean syllable, every dialogue
renderer family, or every menu surface is ready for release.

The next font gate is per scene batch:

1. Generate only the glyphs used by that batch.
2. Verify the changed CHR slots and text bytes are within the allowlist.
3. Capture the scene through its bounded route.
4. Record `PASS`, `FAIL`, or `UNKNOWN` before promoting the batch.

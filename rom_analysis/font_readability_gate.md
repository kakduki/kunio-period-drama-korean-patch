# Korean Dialogue Font Readability Gate

Status: **PASS_FOR_OPENING_PAIRED_16X16_EXPANDED_RECORD**

This development gate measures a real native dialogue frame. It is not a
release gate and it does not authorize bulk translation.

| candidate | native scene | runtime result | readability result | decision |
| --- | --- | --- | --- | --- |
| 8x8 raster baseline | opening dialogue, frame 883 | target record display pass | FAIL: syllables are too compressed | structural baseline only |
| 8x16 vertical-pair proof | same scene and frame | bounded boot and target reads pass | FAIL at the Korean-quality bar: still too narrow | technical building block only |
| paired 8x16 cells, eight syllables | same scene and frame | 37/37 reads and capture pass | PASS: proof glyphs, punctuation, and spaces are distinguishable | provisional 16x16 renderer direction |
| paired 16x16 Tier 1 | same scene and frame | 37/37 reads and capture pass | PASS: 13 syllables remain distinct | source-pool expansion evidence |
| paired 16x16 Tier 2 | same scene and frame | 37/37 reads and capture pass | PASS: all 17 syllables, including `0xC0-0xC7`, are distinct | capacity evidence; compact text only |
| paired 16x16 expanded record | same scene and frame | 45/45 reads, `lua_done`, and capture pass | PASS: `쿠니마사 어서 움직여!` / `분조 두목이 큰일이야!` is readable with preserved spaces and no visible scene damage | opening record and relocation proof |

## Evidence

- 16x16 first proof crop: `rom_analysis/opening_dialogue_16x16_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Tier 1 capture: `rom_analysis/opening_dialogue_16x16_capacity_tier1_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Tier 2 capture: `rom_analysis/opening_dialogue_16x16_capacity_tier2_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Expanded-record full screen: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/opening_dialogue_frame_000883_screen.png`
- Expanded-record 4x crop: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Expanded-record smoke report: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/analysis.md`
- Expanded-record runtime bytes: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/opening_target_record.tsv`

The route ends at frame 883 with `lua_done`. It is not an autoplay session and
does not wait for later gameplay or boss events.

## Scope Limit

This pass covers one dialogue renderer, pointer 182, and one opening screen.
The 17-syllable allocation uses 34 source slots and is a scene-local proof, not
a complete Korean character set. The relocated pointer-183 record is statically
preserved, but its own on-screen result is `UNKNOWN` until a separate bounded
capture reaches it.

## Next Gate

1. Design an expanded dialogue code layout that preserves the special `0xBB`
   speaker separator while retaining Korean source slots.
2. Establish a multi-scene glyph capacity strategy before translating batches.
3. Verify each pointer relocation both statically and in its own screen context.
4. Move to title/menu and item/status renderers only through deterministic,
   bounded routes or save/debug states.

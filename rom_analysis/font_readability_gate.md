# Korean Dialogue Font Readability Gate

Status: **PASS_FOR_TWO_OPENING_CONTEXTS_ONLY**

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
| paired 16x16 speaker separator | same scene and frame | 47/47 reads, `lua_done`, and capture pass | PASS: `쿠니마사: 어서 움직여!` / `분조 두목이 큰일이야!` keeps the name, colon, spaces, and punctuation distinct | opening speaker-separator proof only |
| paired 16x16 readable profile | same scene and frame | 38/38 reads, `lua_done`, and capture pass | PASS: 14-pixel Malgun Gothic Bold with BOX resampling retains interior whitespace and keeps both Korean lines legible | preferred opening readability prototype only |
| two-record opening candidate | pointer 182 frame 883; pointer 183 frame 1095 | 33/33 and 25/25 reads, `lua_done`, and captures pass | PASS: both Korean dialogue screens are legible; pointer 183 preserves the native `0xBB` speaker separator and adds normal spacing | two verified opening contexts only |

## Evidence

- 16x16 first proof crop: `rom_analysis/opening_dialogue_16x16_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Tier 1 capture: `rom_analysis/opening_dialogue_16x16_capacity_tier1_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Tier 2 capture: `rom_analysis/opening_dialogue_16x16_capacity_tier2_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Expanded-record full screen: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/opening_dialogue_frame_000883_screen.png`
- Expanded-record 4x crop: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Expanded-record smoke report: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/analysis.md`
- Expanded-record runtime bytes: `rom_analysis/opening_dialogue_16x16_relocation_proof_capture/opening_target_record.tsv`
- Speaker-separator full screen: `rom_analysis/opening_dialogue_16x16_speaker_separator_proof_capture/opening_dialogue_frame_000883_screen.png`
- Speaker-separator 4x crop: `rom_analysis/opening_dialogue_16x16_speaker_separator_proof_capture/opening_dialogue_frame_000883_screen_dialogue_box_4x.png`
- Speaker-separator smoke report: `rom_analysis/opening_dialogue_16x16_speaker_separator_proof_capture/analysis.md`
- Readability-profile comparison: `rom_analysis/opening_font_profile_comparison/profiles.png`
- Readability-profile metrics: `rom_analysis/opening_font_profile_comparison/report.md`
- Readability-profile full screen: `rom_analysis/opening_dialogue_16x16_readability_proof_capture/opening_dialogue_frame_000883_screen.png`
- Readability-profile smoke report: `rom_analysis/opening_dialogue_16x16_readability_proof_capture/analysis.md`
- Two-record pointer-182 screenshot: `rom_analysis/opening_ptr_182_183_16x16_p182_capture/opening_dialogue_frame_000883_screen.png`
- Two-record pointer-182 smoke report: `rom_analysis/opening_ptr_182_183_16x16_p182_capture/analysis.md`
- Two-record pointer-183 screenshot: `rom_analysis/opening_ptr_182_183_16x16_p183_capture/opening_dialogue_frame_001095_screen.png`
- Two-record pointer-183 smoke report: `rom_analysis/opening_ptr_182_183_16x16_p183_capture/analysis.md`

The route ends at frame 883 with `lua_done`. It is not an autoplay session and
does not wait for later gameplay or boss events.

## Scope Limit

This pass covers one dialogue renderer and two opening screens, pointer 182
and pointer 183. The 19-glyph allocation includes a local 16x16 colon for
pointer 182 and remains a scene-local proof, not a complete Korean character
set. The raw `0xBB` separator is preserved and visibly works in pointer 183;
it remains a control token rather than an allocatable Korean glyph slot.

### Readability-Profile Scope

The earlier 15-glyph readability allocation is superseded by the 19-glyph
two-record candidate for these two contexts. Neither allocation is a complete
Korean character set. The frame-883 and frame-1095 routes are regression
targets only; they must not be repeated as a way to search for later scenes.

## Next Gate

1. Design a release-wide dialogue code layout that preserves raw control tokens
   while retaining Korean source slots.
2. Establish a multi-scene glyph capacity strategy before translating batches.
3. Verify each pointer relocation both statically and in its own screen context.
4. Move to title/menu and item/status renderers only through deterministic,
   bounded routes or save/debug states.
5. Do not repeat the frame-883 opening route unless a specifically changed
   pointer-182 candidate needs regression evidence.

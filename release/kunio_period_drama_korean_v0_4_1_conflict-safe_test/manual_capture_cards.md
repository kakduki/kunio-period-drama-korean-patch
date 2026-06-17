# Manual Capture Cards

Use these short cards at the FCEUX window. They are intentionally smaller than the full decision matrix.

- Stop blind autoplay when `stagnant_screen` appears.
- Pause on the exact text/menu/status screen before running Lua.
- Keep the generated dumps as evidence even when there is no active match.

## Task 1: `0x06295`

- Kind: `conflict_needs_manual_screen`
- Source/Korean: カタナ -> 카타나
- Evidence/Risk: static-candidate+pointer / safe-equal-length
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Purpose: Confirm original-byte broad-scan evidence before building a new patch candidate.
- Decision after capture: Use base ROM broad-scan dump first, then decide whether to keep v0.4.1 exclusion or replace with broad interpretation.

## Task 2: `0x0631C`

- Kind: `conflict_needs_manual_screen`
- Source/Korean: カタナ -> 카타나
- Evidence/Risk: static-candidate+pointer / safe-equal-length
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Purpose: Confirm original-byte broad-scan evidence before building a new patch candidate.
- Decision after capture: Use base ROM broad-scan dump first, then decide whether to keep v0.4.1 exclusion or replace with broad interpretation.

## Task 3: `0x0635A`

- Kind: `conflict_needs_manual_screen`
- Source/Korean: カタナ -> 카타나
- Evidence/Risk: static-candidate / safe-equal-length
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Purpose: Confirm original-byte broad-scan evidence before building a new patch candidate.
- Decision after capture: Use base ROM broad-scan dump first, then decide whether to keep v0.4.1 exclusion or replace with broad interpretation.

## Task 4: `0x05644`

- Kind: `local_overlap_needs_manual_screen`
- Source/Korean: カタナ -> 카타나
- Evidence/Risk: static-candidate+pointer / safe-equal-length
- Open ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.nes`
- Run Lua: `lua/kunio_manual_v041_screen_dump.lua`
- Summarize: `python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v041 --output rom_analysis/manual_screen_dump_v041/summary.md`
- Purpose: Verify the current conflict-safe candidate on the manually reached screen.
- Decision after capture: Manually capture this exact screen; the nearby applied row may represent a different overlapping interpretation.

## Task 5: `0x071A4`

- Kind: `runtime_padding_rule_blocker`
- Source/Korean: ちから -> 힘
- Evidence/Risk: runtime-confirmed / needs-padding-rule
- Open ROM: `output/kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_00.nes first, then compare other padding experiment ROMs`
- Run Lua: `lua/kunio_manual_screen_dump.lua`
- Summarize: `python scripts/analyze_manual_screen_dump.py`
- Purpose: Decide which padding strategy renders cleanly before shortening this text.
- Decision after capture: Test padding experiment ROMs visually on the same status screen before promoting a shortened replacement.

## Task 6: `0x0440C`

- Kind: `broad_non_overlapping`
- Source/Korean: かじや -> 대장간
- Evidence/Risk: medium / safe-equal-length after screen proof
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Purpose: Confirm original-byte broad-scan evidence before building a new patch candidate.
- Decision after capture: Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment.

## Task 7: `0x048F4`

- Kind: `broad_non_overlapping`
- Source/Korean: たつじ -> 타츠지
- Evidence/Risk: medium / safe-equal-length after screen proof
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Purpose: Confirm original-byte broad-scan evidence before building a new patch candidate.
- Decision after capture: Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment.

## Task 8: `0x052A5`

- Kind: `broad_non_overlapping`
- Source/Korean: たつじ -> 타츠지
- Evidence/Risk: medium / safe-equal-length after screen proof
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Purpose: Confirm original-byte broad-scan evidence before building a new patch candidate.
- Decision after capture: Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment.

## Task 9: `0x05BE5`

- Kind: `broad_non_overlapping`
- Source/Korean: たつじ -> 타츠지
- Evidence/Risk: medium / safe-equal-length after screen proof
- Open ROM: `rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Run Lua: `lua/kunio_manual_broad_scan_dump.lua`
- Summarize: `python scripts/analyze_broad_scan_manual_dump.py`
- Purpose: Confirm original-byte broad-scan evidence before building a new patch candidate.
- Decision after capture: Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment.

## Task 10: `0x05BBA`

- Kind: `wrong_context_or_padding_candidate`
- Source/Korean: やり -> 창
- Evidence/Risk: static-candidate+pointer / needs-padding-rule
- Open ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.nes`
- Run Lua: `lua/kunio_manual_v041_screen_dump.lua`
- Summarize: `python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v041 --output rom_analysis/manual_screen_dump_v041/summary.md`
- Purpose: Verify the current conflict-safe candidate on the manually reached screen.
- Decision after capture: Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context.

## Task 11: `0x06001`

- Kind: `wrong_context_or_padding_candidate`
- Source/Korean: やり -> 창
- Evidence/Risk: static-candidate / needs-padding-rule
- Open ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.nes`
- Run Lua: `lua/kunio_manual_v041_screen_dump.lua`
- Summarize: `python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v041 --output rom_analysis/manual_screen_dump_v041/summary.md`
- Purpose: Verify the current conflict-safe candidate on the manually reached screen.
- Decision after capture: Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context.

## Task 12: `0x0602E`

- Kind: `wrong_context_or_padding_candidate`
- Source/Korean: そうび -> 장비
- Evidence/Risk: static-candidate+pointer / needs-padding-rule
- Open ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.nes`
- Run Lua: `lua/kunio_manual_v041_screen_dump.lua`
- Summarize: `python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v041 --output rom_analysis/manual_screen_dump_v041/summary.md`
- Purpose: Verify the current conflict-safe candidate on the manually reached screen.
- Decision after capture: Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context.

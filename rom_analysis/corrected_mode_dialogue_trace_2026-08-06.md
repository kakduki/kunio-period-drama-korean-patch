# Corrected Mode-Selection Dialogue Trace

Date: 2026-08-06

## Purpose

The earlier bounded route treated the frame-900 mode-selection screen as combat. The shared stage probe now supports `KUNIO_SELECT_MODE=1` and `KUNIO_ADVANCE_OPENING_DIALOGUE=1`, so the run confirms `1P ? COM`, waits for field entry, and advances the opening event with bounded A/Start pulses.

## Run

- ROM: verified Japanese base, MD5 `0d406a85285b4de8468f0dab6aad5fe5`
- Probe: `lua/kunio_stage_progression_probe.lua`
- Frames: 2,400
- Completion: `lua_done`
- Output: `C:/tmp/kunio_corrected_dialogue_trace_2026_08_06`

## Evidence

- Unique screen fingerprints: 23
- `dialogue_source_reads.tsv`: 140 rows
- `dialogue_parser_exec.tsv`: 204 rows
- `dialogue_pointers.tsv`: includes opening-event pointers such as `AE02` with stream pointer `94B5`, followed by `8080`/`8201` stream activity
- `dialogue_ppu_writes.tsv`: no dialogue-specific rows in this run; the broad `ppu_writes.tsv` trace reached its configured 24,000-row cap
- The run did not reach a proven boss transition or natural enemy-clear event

## Classification

`PASS_MODE_SELECT_AND_DIALOGUE_RUNTIME_TRACE; UNKNOWN_NATIVE_DIALOGUE_VISUAL_GATE`

This is stronger than the previous opening-only interpretation: the emulator selects the intended single-player mode and executes the dialogue parser/source-read path. It is not yet proof that the Korean candidate renders this later dialogue on the native lower dialogue band, so no new translation row is promoted from this trace.

# Real-Time Translation Overlay MVP Result

Date: 2026-08-05

## Bounded Runtime

The emitter was run against the verified Japanese base ROM with a 1,000-frame
ceiling. It used the existing bounded FCEUX launcher and the proven pointer
182 opening source record.

```text
python scripts/run_fceux_lua_analysis.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\kunio_translation_overlay.lua --target-lua lua\kunio_translation_overlay_targets.lua --frames 1000 --timeout 90 --final-output C:\tmp\kunio_overlay_runtime --clean-output --no-dump-hex --no-dump-bin --lua-env KUNIO_OVERLAY_OUTPUT=kunio_fceux_lua_output --lua-env KUNIO_OVERLAY_TARGETS_LUA=kunio_translation_overlay_targets.lua
```

Result:

- Emulator completion: `lua_done`
- Registered target bytes: `33`
- Events: `1`
- Event: `OPENING-182` at frame `656`
- Context: `pointer_182_opening`
- Receiver status: `CACHED`
- Translation source: `translation/script.csv`
- ROM modification: none

The event file was then resolved with:

```text
python tools/realtime_translation_overlay.py --events C:\tmp\kunio_overlay_runtime\events.tsv --cache translation\script.csv --once
```

This proves the complete MVP path for one known string: FCEUX source-read
event -> TSV handoff -> Korean cache lookup -> overlay text resolution. It is
not evidence that unknown strings are automatically translated or that a
native Korean ROM patch is release-ready.

## Usage

Start the bounded emitter from FCEUX with
`lua/kunio_translation_overlay.lua`, then run the receiver without `--once`:

```text
python tools/realtime_translation_overlay.py --events rom_analysis/realtime_overlay/events.tsv --cache translation/script.csv
```

For an uncached event, an optional translator command may be supplied. The
command receives one JSON object on stdin and must print one translated line.
Its output is marked `AI_UNCHECKED` and is not written into the ROM or promoted
to the translation manifest automatically.

# Real-Time Translation Overlay MVP Result

Date: 2026-08-05

## Bounded Runtime

The emitter was run against the verified Japanese base ROM with a 1,500-frame
ceiling. It used the existing bounded FCEUX launcher and three verified opening
pointer source records (182-184).

```text
python scripts/run_fceux_lua_analysis.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\kunio_translation_overlay.lua --target-lua lua\kunio_translation_overlay_targets.lua --frames 1500 --timeout 90 --final-output C:\tmp\kunio_overlay_runtime_v2 --clean-output --no-dump-hex --no-dump-bin --lua-env KUNIO_OVERLAY_OUTPUT=kunio_fceux_lua_output --lua-env KUNIO_OVERLAY_TARGETS_LUA=kunio_translation_overlay_targets.lua
```

Result:

- Emulator completion: `lua_done`
- Registered target bytes: `81` across `3` targets
- Events: `3` total, covering `2` distinct IDs
- `OPENING-182`: frame `656`
- `OPENING-183`: frames `718` and `1047`
- `OPENING-184`: no event before the frame cap; `UNKNOWN_ROUTE_NOT_REACHED`
- Receiver status for the latest event: `CACHED`
- Translation source: `translation/realtime_overlay.csv`
- ROM modification: none

The event file was then resolved with:

```text
python tools/realtime_translation_overlay.py --events C:\tmp\kunio_overlay_runtime_v2\events.tsv --cache translation\realtime_overlay.csv --once
```

This proves the complete MVP path for the two reached known strings: FCEUX
source-read event -> TSV handoff -> Korean cache lookup -> overlay text
resolution. The third target is registered but still route-unknown. This is
not evidence that unknown strings are automatically translated or that a
native Korean ROM patch is release-ready.

## Usage

Start the bounded emitter from FCEUX with
`lua/kunio_translation_overlay.lua`, then run the receiver without `--once`:

```text
python tools/realtime_translation_overlay.py --events rom_analysis/realtime_overlay/events.tsv
```

The receiver defaults to `translation/realtime_overlay.csv`. For an uncached
event, an optional translator command may be supplied. The command receives
one JSON object on stdin and must print one translated line. Its output is
marked `AI_UNCHECKED` and is not written into the ROM or promoted to the
translation manifest automatically.

## Expanded Four-Record Recheck (2026-08-05)

The overlay target table was corrected for pointer 184 to use its exact base
source window (`0x071F0`, `$B1E0-$B1F7`) and expanded with pointer 185.
The bounded emitter was then run with a 1,900-frame ceiling:

```text
python scripts/run_fceux_lua_analysis.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --lua-script lua\kunio_translation_overlay.lua --target-lua lua\kunio_translation_overlay_targets.lua --frames 1900 --timeout 60 --final-output C:\tmp\kunio_overlay_runtime_p185_v2 --clean-output --no-dump-hex --no-dump-bin --lua-env KUNIO_OVERLAY_OUTPUT=kunio_fceux_lua_output --lua-env KUNIO_OVERLAY_TARGETS_LUA=kunio_translation_overlay_targets.lua
```

- Emulator completion: `lua_done` at frame `1900`
- Registered target bytes: `97` across `4` targets
- Events: `5` total covering `4` IDs
- `OPENING-182`: frame `656`
- `OPENING-183`: frames `718`, `1047`
- `OPENING-184`: frame `1349`
- `OPENING-185`: frame `1655`
- Receiver lookup: `OPENING-185` resolved as `CACHED`
- ROM modification: none

This is a bounded four-record sidecar proof. It does not prove full-game
coverage or native Korean visual safety. The p185 Korean text is a reviewed
draft (`오코토: 이 사람은`) and remains separate from release approval.

## Fourteen-Record Cache Sync (2026-08-07)

`translation/realtime_overlay.csv` and
`lua/kunio_translation_overlay_targets.lua` now cover the same fourteen
opening rows already promoted in `translation/script.csv`
(`OPENING-182` through `OPENING-195`). Pointers 186-193 use the Japanese
Bank 1 source windows from `rom_analysis/pointer_dialogue_catalog.tsv`.
Pointers 196-197 remain excluded until a natural route reaches them.

This is a sidecar cache/target sync only. It does not change native ROM
release status, which remains `NOT_READY`. A bounded FCEUX emitter recheck
still requires the verified Japanese base ROM in `rom/`.

# FCEUX Bank 1 read-watch test summary

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua\kunio_bank1_watch.lua --frames 900 --timeout 90 --final-output rom_analysis\fceux_bank1_watch_test --clean-output --no-dump-hex --no-dump-bin
```

Result:

- Lua completed automatically at frame `900`.
- `memory.registerread` callback mode was available.
- Registered watched CPU addresses: `124`.
- Total read hits: `247`.

Observed labels:

| label | category | ROM hit | CPU record range | hits | first frame | last frame | evidence |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `chikara_stat_e` | stat | `ROM+0x071A4` | `$B192-$B19C` | 11 | 358 | 376 | Context includes bytes `93 88 AA`, matching the `ちから` candidate. |
| `soubi_ui_c` | ui | `ROM+0x06FA1` | `$AF91-$AF9A` | 236 | 604 | 802 | The watched range is repeatedly read during the short auto-progress run. |

Notes:

- This does not prove every Bank 1 candidate yet, but it confirms that the new watcher runs inside FCEUX and that at least two candidate records are read at runtime.
- The raw TSV files from this short test were not committed; rerun the command above to regenerate them.

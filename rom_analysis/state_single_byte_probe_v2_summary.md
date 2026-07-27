# State Single-Byte Probe v2 Summary

Status: **UNKNOWN_ROUTE_STATE**

The top four runtime-flag candidates were tested one at a time with the
existing bounded input route:

| address | value | frames | screen fingerprints | result |
| --- | --- | ---: | --- | --- |
| `$0720` | `B1` | 2400 | `877702039:25800`, `206542110:45120`, `972456399:45600`, `980998441:26760`, `323851653:39240` | UNKNOWN; no boss/event transition |
| `$0721` | `45` | 2400 | same route fingerprints | UNKNOWN; no boss/event transition |
| `$0722` | `C9` | 2400 | same route fingerprints | UNKNOWN; no boss/event transition |
| `$0723` | `7A` | 2400 | route ended at `206542110:45120` | UNKNOWN; no boss/event transition |

Each run wrote only the named byte during frames `520-1900`, captured screen
dumps on fingerprint changes, and ended at the hard frame budget. The values
are therefore not promoted as scene-warp, enemy-clear, or boss-spawn cheats.
The raw FCEUX dumps remain local and ignored; this compact result is the
check-in evidence.

The next state probe should use object/route addresses or a known save/debug
state, not more writes to these four changing runtime flags.

## Object Block Follow-Up

The recommended `$04F0` paired write was also tested:

`$04FA=30, $04F1=02, $04FB=31, $04FC=32`

At the same 2,400-frame bound it produced the same route fingerprints and no
boss/event transition. The block remains an object-state candidate only; it is
not promoted as an enemy-clear or scene-warp cheat.

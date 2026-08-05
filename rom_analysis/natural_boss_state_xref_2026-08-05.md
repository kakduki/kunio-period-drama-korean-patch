# Natural boss-state xref classification (2026-08-05)

This report classifies the RAM addresses that were previously considered as possible enemy-clear or boss-transition cheats. The static scan is a candidate classifier, not a disassembly proof by itself; runtime evidence is required before any patch.

Command:

```text
python scripts/analyze_ram_xrefs.py <verified Japanese base ROM> --targets 0x04F1,0x04FA,0x04FB,0x04FC,0x0502,0x0503,0x0506,0x0508,0x0509,0x0706,0x0700,0x02A8,0x02AC,0x02B0,0x02B4,0x02B8,0x02BC
```

## Classifications

- `$0502/$0503`: fixed-bank code uses these as mapper configuration data around `$D228` and `$EE3F-$EE59`; not an enemy HP candidate.
- `$0506`: fixed-bank code initializes and increments this at `$E39A-$E43C`; the surrounding loop is a bounded screen/operation counter. It is not a confirmed enemy-clear counter.
- `$0508`: references at bank 4 `$806C/$812F/$8422/$8428` are runtime object/render bookkeeping. The prior PC trace showed repeated coordinate-like updates, not damage depletion.
- `$04FA-$04FD`: references are spread across dialogue/state setup and renderer metadata paths, including `$D1B3-$D242` and `$E8C2-$EC7F`. Prior runtime writes were short metadata updates; no HP semantics were proven.
- `$0700/$0706`: broad object/item workspace references; `$0706` has a fixed-bank `DEC` at `$8B0A`, but the existing route traces identify it as slot iteration, not a clear marker.
- `$02A8-$02BC`: no useful absolute indexed HP references were found; prior PC-tagged writes were position/render fields.

## Decision

`UNKNOWN_NO_CONFIRMED_BOSS_STATE_XREF`. No address from this set is promoted to a cheat or ROM patch. The natural boss/event route remains open. The next diagnostic should trace the combat collision/damage routine and its branch target, then compare a real hit against a miss before attempting any state write.
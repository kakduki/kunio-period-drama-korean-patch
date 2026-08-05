# English Reference Combat Route Comparison (2026-08-06)

## Purpose

The English IPS is a structural reference, so the same bounded controller route
was run against the English reference ROM and the verified Japanese base. This
checks whether the current failure to reach enemy collision is introduced by
localization work or is already present in the route itself.

## Runtime Matrix

| ROM | frames | completion | unique screens | FC65 scans | FAD9 collision | FC82 dispatch | FCEF clears | final fingerprint |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Japanese base | 3,600 | lua_done | 11 | 1,234 | 0 | 0 | 0 | 553498214:7247 |
| English reference | 3,600 | lua_done | 11 | 1,234 | 0 | 0 | 0 | 553498214:7247 |

Both runs used `lua/kunio_stage_progression_probe.lua`, `KUNIO_EXTRA_DIALOGUE_START=1`,
`KUNIO_COMBAT_MIXED=1`, and the optional slot/collision execution trace. The
English reference ROM was `output/english_reference_runtime/kunio_period_drama_english_reference.nes`.

## Conclusion

`PASS_SAME_ROUTE_SHAPE_NO_COLLISION`

The English patch does not make this automated route reach a real enemy battle,
and the Korean work is not the cause of the repeated bounded combat pattern.
The route reaches actor/field processing and the FC65 scan, but no collision
selection or slot-clear routine. The English IPS remains useful for text,
pointer, renderer, and font architecture; it does not supply a boss warp or a
complete gameplay macro.

Natural enemy-clear, map progression, boss dialogue, save/load, ending, and
full-game regression remain `UNKNOWN`. No cheat or ROM candidate is promoted
from this comparison.
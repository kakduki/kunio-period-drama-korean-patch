# Combat Slot-Clear Trace (2026-08-06)

## Purpose

The fixed-bank routine at FC65 scans object/player slots 0-3 and 4-6. Its
branch target FCEF clears slot status and object fields. This trace checks
whether the current bounded input routes actually reach that clear path.

Static observations from the Japanese base:

- FC65 scans slot groups and conditionally calls FCEF.
- FCEF clears 04AC,X, 0049,X, and 0050,X, marks 0496,X, and may continue
  through FD49 for an active object.
- EF85 increments 0506; EF88 increments 0509 and carries into 050A/050B.
  These are frame/operation counters, not proven enemy-clear variables.

## Runtime Matrix

| route | frames | completion | FC65 scans | FCEF slot clears | transition checks |
| --- | ---: | --- | ---: | ---: | ---: |
| mixed | 7200 | lua_done | 2914 | 0 | 0 |
| grid | 3600 | lua_done | 1212 | 0 | 0 |
| stationary | 3600 | lua_done | 1237 | 0 | 0 |

All runs used the verified Japanese base and the bounded stage progression
probe. The mixed run produced 13 unique screen fingerprints; the other runs
also completed without a launcher timeout.

## Classification

PASS_NO_SLOT_CLEAR_REACHED

The input sweeps enter and animate the bounded combat route, but none proves a
real enemy hit/death or a boss transition. No slot byte, counter, or ROM branch
is promoted as a cheat. The natural boss route and later dialogue remain
UNKNOWN_NOT_REACHED.

This result explains why longer autoplay repeats a finite combat/interaction
pattern: it never reaches the slot-clear event that would advance the
encounter. The realtime overlay/manual launcher is therefore the correct next
collection path for unknown scenes, while native patch promotion still requires
runtime source/PPU proof.
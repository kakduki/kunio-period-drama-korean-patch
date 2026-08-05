# Combat State Pair Read Trace

Date: 2026-08-06

## Purpose

This trace tests whether $04F1 is a safe enemy-clear or boss-transition cheat target. It does not modify RAM and is bounded by both frame count and trace-row count.

## Runtime

Base candidate: the 244-row full-pointer Korean candidate ROM.

Probe settings: KUNIO_MAX_FRAMES=2400, KUNIO_EXTRA_DIALOGUE_START=1, KUNIO_COMBAT_SWEEP=1, KUNIO_STATE_READ_TRACE=1, KUNIO_STATE_READ_TRACE_LIMIT=12000.

Output: C:\tmp\kunio_state_pair_trace_2400_2026_08_06\state_reads.tsv

The emulator completed with lua_done.

## Observations

| Address | Reads | Dominant PC | Dominant role |
| --- | ---: | --- | --- |
| $04F1 | 692 | $DDDF | compare against $04F3 |
| $04F3 | 646 | $DDE2 | comparison partner |
| $04F2 | 732 | $DDFC | compare against $04F4 |
| $04F4 | 648 | $DDFF | comparison partner |

During combat, the observed values were stable at $04F1=$01, $04F3=$01, $04F2=$00, and $04F4=$00.

The fixed-bank code compares $04F1 with $04F3 and $04F2 with $04F4. Writing $04F1 alone would break a synchronized pair or be overwritten by normal state initialization; it is not a justified boss transition cheat.

## Classification

PASS_TRACE_NOT_A_SAFE_CHEAT_TARGET

This is negative evidence. The $04F1 single-byte candidate is excluded from promotion and release patches. No boss spawn or later boss dialogue was proven by this run.

## Next Investigation

Continue with the documented map/event route and inspect the $7A02 counter and object/event state together. Any candidate must show a reproducible state transition and finite completion before targeted dialogue capture.
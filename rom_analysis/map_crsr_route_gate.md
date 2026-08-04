# Map CRSR Route Gate

Date: 2026-08-05

## Confirmed Facts

- English pre-pointer record: `EN-PRE-167`
- ROM offset: `0x05C69`
- Bank 1 CPU address by the project mapping formula: `$9C59`
- Bytes: `8D 81 90 38 83 92 93 92 FF`
- English label: `MAP<38>CRSR<FF>`
- The byte `0x38` is an explicit control code, so this is not a plain text-only record.

A bounded regeneration of the standard pre-pointer runtime target table produced
`168` targets and skipped `61` `control_skeleton` rows. `EN-PRE-167` was not
included. This is an evidence boundary, not proof that the label is unreachable.

## Important Non-Equivalence

The generated Bank 1 candidate list contains a row labelled `rom_05c69_candidate_7a`
at CPU `$9C54-$9C5C` with bytes `9F A3`. That address and byte pattern are
not the `EN-PRE-167` record at `$9C59-$9C61`; the label must not be used as
an authorization to patch or write `$9C54`.

The pointer dialogue catalog separately contains `PTR-237` with the English
instruction `USE MAP CURSOR TO TRAVEL`, but that proves only a dialogue record,
not possession of the Map CRSR item or a safe RAM ownership address.

## Current Decision

- Map CRSR state: `UNKNOWN`
- Safe RAM ownership address: not proven
- State-write cheat: not authorized
- Native patch change: none

The next valid evidence is a source-read/code trace from the actual shop or map
item path, or a save/state comparison that changes only the Map CRSR ownership
state. Random writes to `$04xx`, `$05xx`, or `$07xx` remain excluded.

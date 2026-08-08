# Pointer Dialogue Korean Draft Audit

Status: **FULL_DRAFT_CAPACITY_BLOCKED**

This report joins the 248-entry English-guided pointer ownership map
with a separate Korean semantic draft. It is a build-planning artifact,
not a release translation approval.

## Coverage

- Draft rows: `248`; active translation rows: `244`; excluded: `4`.
- Translation statuses: `{'english_reference_reviewed': 244, 'excluded_non_dialogue': 4}`.
- Basis: `{'english_reference': 248}`.

## Capacity Gate

- Proven direct dialogue source pool: `0x81-0x9A plus 0xC0-0xC7 (opening p182)` (34 codes).
- Draft unique non-space symbols: `378`.
- Capacity gap: `344` symbols.
- Static font map misses `220` of the draft symbols.
- The full build is blocked until the renderer has a multi-page or scene-local font strategy, or the Korean wording is reduced to a proven pool.

## Space Estimate

- Estimated compiled bytes: `3917`; original active record bytes: `5998`.
- Estimated packed end: `0x06F34` inside the broad Bank-1 window.
- Records longer than their original in-place span: `21`.
- This is a relocation feasibility estimate only. A builder must still check every pointer owner, protected record, and code/data boundary.

## Suggested Batches

The batches below are greedy capacity groups using the currently proven 34-code opening pool; they are not automatically approved patch targets.

| batch | pointer indices | records | unique symbols |
| ---: | --- | ---: | ---: |
| 1 | `0-3` | 4 | 34 |
| 2 | `4-6` | 3 | 26 |
| 3 | `7-10` | 4 | 28 |
| 4 | `11-15` | 5 | 33 |
| 5 | `16-19` | 4 | 34 |
| 6 | `20-22` | 3 | 30 |
| 7 | `23-25` | 3 | 30 |
| 8 | `26-27` | 2 | 26 |
| 9 | `28-30` | 3 | 32 |
| 10 | `31-34` | 4 | 29 |
| 11 | `35-37` | 3 | 24 |
| 12 | `38-40` | 3 | 32 |
| 13 | `41-44` | 4 | 32 |
| 14 | `45-46` | 2 | 24 |
| 15 | `47-49` | 3 | 32 |
| 16 | `50-53` | 4 | 33 |
| 17 | `54-55` | 2 | 27 |
| 18 | `56-59` | 4 | 28 |
| 19 | `60-62` | 3 | 32 |
| 20 | `63-66` | 4 | 30 |
| 21 | `67-68` | 2 | 28 |
| 22 | `69-71` | 3 | 33 |
| 23 | `72-75` | 4 | 34 |
| 24 | `76-77` | 2 | 21 |
| 25 | `78-79` | 2 | 27 |
| 26 | `80-81` | 2 | 28 |
| 27 | `82-85` | 4 | 33 |
| 28 | `86-87` | 2 | 26 |
| 29 | `88-90` | 3 | 34 |
| 30 | `91-94` | 4 | 26 |
| 31 | `95-97` | 3 | 32 |
| 32 | `98-101` | 4 | 32 |
| 33 | `102-104` | 3 | 28 |
| 34 | `105-107` | 3 | 33 |
| 35 | `108-109` | 2 | 25 |
| 36 | `110-116` | 7 | 32 |
| 37 | `117-122` | 6 | 32 |
| 38 | `123-134` | 12 | 34 |
| 39 | `135-140` | 6 | 34 |
| 40 | `141-147` | 7 | 33 |
| 41 | `148-155` | 8 | 32 |
| 42 | `156-164` | 8 | 31 |
| 43 | `165-166` | 2 | 29 |
| 44 | `167-169` | 3 | 31 |
| 45 | `170-172` | 3 | 25 |
| 46 | `173-175` | 3 | 30 |
| 47 | `176-178` | 3 | 32 |
| 48 | `179-181` | 3 | 26 |
| 49 | `182-185` | 4 | 28 |
| 50 | `186-188` | 3 | 31 |
| 51 | `189-191` | 3 | 31 |
| 52 | `192-197` | 6 | 33 |
| 53 | `198-202` | 5 | 33 |
| 54 | `203-205` | 3 | 34 |
| 55 | `206-207` | 2 | 30 |
| 56 | `208-213` | 6 | 30 |
| 57 | `214-215` | 2 | 23 |
| 58 | `216-219` | 4 | 26 |
| 59 | `220-221` | 2 | 22 |
| 60 | `222-225` | 4 | 31 |
| 61 | `226-230` | 5 | 31 |
| 62 | `231-237` | 7 | 34 |
| 63 | `238-245` | 7 | 32 |

The next compiler may consume one of these batches only after its Korean wording, control bytes, renderer family, and bounded runtime target are declared.

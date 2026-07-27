# Pointer Dialogue Korean Draft Audit

Status: **FULL_DRAFT_CAPACITY_BLOCKED**

This report joins the 248-entry English-guided pointer ownership map
with a separate Korean semantic draft. It is a build-planning artifact,
not a release translation approval.

## Coverage

- Draft rows: `248`; active translation rows: `244`; excluded: `4`.
- Translation statuses: `{'english_semantic_draft': 244, 'excluded_non_dialogue': 4}`.
- Basis: `{'english_reference': 248}`.

## Capacity Gate

- Proven direct dialogue source pool: `0x81-0x9A plus 0xC0-0xC7 (opening p182)` (34 codes).
- Draft unique non-space symbols: `378`.
- Capacity gap: `344` symbols.
- Static font map misses `246` of the draft symbols.
- The full build is blocked until the renderer has a multi-page or scene-local font strategy, or the Korean wording is reduced to a proven pool.

## Space Estimate

- Estimated compiled bytes: `4001`; original active record bytes: `5998`.
- Estimated packed end: `0x06F88` inside the broad Bank-1 window.
- Records longer than their original in-place span: `26`.
- This is a relocation feasibility estimate only. A builder must still check every pointer owner, protected record, and code/data boundary.

## Suggested Batches

The batches below are greedy capacity groups using the currently proven 34-code opening pool; they are not automatically approved patch targets.

| batch | pointer indices | records | unique symbols |
| ---: | --- | ---: | ---: |
| 1 | `0-3` | 4 | 34 |
| 2 | `4-7` | 4 | 32 |
| 3 | `8-12` | 5 | 29 |
| 4 | `13-17` | 5 | 30 |
| 5 | `18-19` | 2 | 26 |
| 6 | `20-22` | 3 | 30 |
| 7 | `23-25` | 3 | 30 |
| 8 | `26-28` | 3 | 34 |
| 9 | `29-31` | 3 | 33 |
| 10 | `32-35` | 4 | 30 |
| 11 | `36-38` | 3 | 29 |
| 12 | `39-42` | 4 | 30 |
| 13 | `43-44` | 2 | 22 |
| 14 | `45-46` | 2 | 24 |
| 15 | `47-49` | 3 | 32 |
| 16 | `50-53` | 4 | 33 |
| 17 | `54-55` | 2 | 27 |
| 18 | `56-59` | 4 | 28 |
| 19 | `60-62` | 3 | 33 |
| 20 | `63-66` | 4 | 30 |
| 21 | `67-68` | 2 | 28 |
| 22 | `69-71` | 3 | 33 |
| 23 | `72-75` | 4 | 34 |
| 24 | `76-77` | 2 | 21 |
| 25 | `78-79` | 2 | 27 |
| 26 | `80-81` | 2 | 28 |
| 27 | `82-84` | 3 | 25 |
| 28 | `85-86` | 2 | 21 |
| 29 | `87-88` | 2 | 33 |
| 30 | `89-91` | 3 | 32 |
| 31 | `92-94` | 3 | 19 |
| 32 | `95-96` | 2 | 27 |
| 33 | `97-100` | 4 | 33 |
| 34 | `101-104` | 4 | 32 |
| 35 | `105-107` | 3 | 33 |
| 36 | `108-109` | 2 | 25 |
| 37 | `110-116` | 7 | 32 |
| 38 | `117-122` | 6 | 32 |
| 39 | `123-134` | 12 | 34 |
| 40 | `135-140` | 6 | 34 |
| 41 | `141-147` | 7 | 33 |
| 42 | `148-154` | 7 | 34 |
| 43 | `155-163` | 8 | 32 |
| 44 | `164-166` | 3 | 34 |
| 45 | `167-169` | 3 | 31 |
| 46 | `170-172` | 3 | 25 |
| 47 | `173-175` | 3 | 30 |
| 48 | `176-178` | 3 | 32 |
| 49 | `179-181` | 3 | 28 |
| 50 | `182-185` | 4 | 28 |
| 51 | `186-188` | 3 | 31 |
| 52 | `189-191` | 3 | 31 |
| 53 | `192-197` | 6 | 33 |
| 54 | `198-202` | 5 | 34 |
| 55 | `203-205` | 3 | 34 |
| 56 | `206-207` | 2 | 30 |
| 57 | `208-213` | 6 | 34 |
| 58 | `214-215` | 2 | 22 |
| 59 | `216-219` | 4 | 26 |
| 60 | `220-221` | 2 | 23 |
| 61 | `222-224` | 3 | 29 |
| 62 | `225-228` | 4 | 33 |
| 63 | `229-236` | 8 | 31 |
| 64 | `237-241` | 5 | 28 |
| 65 | `242-245` | 3 | 19 |

The next compiler may consume one of these batches only after its Korean wording, control bytes, renderer family, and bounded runtime target are declared.

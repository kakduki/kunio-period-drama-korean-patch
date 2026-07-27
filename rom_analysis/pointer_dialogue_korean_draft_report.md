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

- Proven direct dialogue source pool: `0x81-0x9A` (26 codes).
- Draft unique non-space symbols: `378`.
- Capacity gap: `352` symbols.
- Static font map misses `246` of the draft symbols.
- The full build is blocked until the renderer has a multi-page or scene-local font strategy, or the Korean wording is reduced to a proven pool.

## Space Estimate

- Estimated compiled bytes: `4001`; original active record bytes: `5998`.
- Estimated packed end: `0x06F88` inside the broad Bank-1 window.
- Records longer than their original in-place span: `26`.
- This is a relocation feasibility estimate only. A builder must still check every pointer owner, protected record, and code/data boundary.

## Suggested Batches

The batches below are greedy capacity groups using the currently proven 26-code pool; they are not automatically approved patch targets.

| batch | pointer indices | records | unique symbols |
| ---: | --- | ---: | ---: |
| 1 | `0-2` | 3 | 24 |
| 2 | `3-4` | 2 | 23 |
| 3 | `5-8` | 4 | 24 |
| 4 | `9-10` | 2 | 19 |
| 5 | `11-14` | 4 | 24 |
| 6 | `15-17` | 3 | 21 |
| 7 | `18-19` | 2 | 26 |
| 8 | `20-20` | 1 | 19 |
| 9 | `21-23` | 3 | 23 |
| 10 | `24-25` | 2 | 23 |
| 11 | `26-27` | 2 | 26 |
| 12 | `28-29` | 2 | 21 |
| 13 | `30-31` | 2 | 25 |
| 14 | `32-34` | 3 | 21 |
| 15 | `35-37` | 3 | 24 |
| 16 | `38-38` | 1 | 19 |
| 17 | `39-41` | 3 | 25 |
| 18 | `42-44` | 3 | 25 |
| 19 | `45-46` | 2 | 24 |
| 20 | `47-47` | 1 | 17 |
| 21 | `48-51` | 4 | 24 |
| 22 | `52-52` | 1 | 13 |
| 23 | `53-54` | 2 | 26 |
| 24 | `55-55` | 1 | 17 |
| 25 | `56-58` | 3 | 18 |
| 26 | `59-60` | 2 | 26 |
| 27 | `61-62` | 2 | 22 |
| 28 | `63-65` | 3 | 26 |
| 29 | `66-67` | 2 | 25 |
| 30 | `68-69` | 2 | 26 |
| 31 | `70-71` | 2 | 21 |
| 32 | `72-73` | 2 | 23 |
| 33 | `74-76` | 3 | 17 |
| 34 | `77-77` | 1 | 16 |
| 35 | `78-78` | 1 | 18 |
| 36 | `79-79` | 1 | 11 |
| 37 | `80-80` | 1 | 17 |
| 38 | `81-83` | 3 | 25 |
| 39 | `84-84` | 1 | 13 |
| 40 | `85-86` | 2 | 21 |
| 41 | `87-87` | 1 | 19 |
| 42 | `88-89` | 2 | 26 |
| 43 | `90-92` | 3 | 24 |
| 44 | `93-94` | 2 | 16 |
| 45 | `95-95` | 1 | 19 |
| 46 | `96-97` | 2 | 22 |
| 47 | `98-100` | 3 | 26 |
| 48 | `101-103` | 3 | 22 |
| 49 | `104-105` | 2 | 23 |
| 50 | `106-107` | 2 | 24 |
| 51 | `108-109` | 2 | 25 |
| 52 | `110-114` | 5 | 25 |
| 53 | `115-120` | 6 | 22 |
| 54 | `121-123` | 3 | 22 |
| 55 | `124-134` | 11 | 26 |
| 56 | `135-137` | 3 | 23 |
| 57 | `138-144` | 7 | 26 |
| 58 | `145-147` | 3 | 25 |
| 59 | `148-152` | 5 | 24 |
| 60 | `153-156` | 4 | 21 |
| 61 | `157-161` | 5 | 22 |
| 62 | `163-164` | 2 | 20 |
| 63 | `165-165` | 1 | 17 |
| 64 | `166-166` | 1 | 18 |
| 65 | `167-168` | 2 | 23 |
| 66 | `169-170` | 2 | 20 |
| 67 | `171-172` | 2 | 16 |
| 68 | `173-174` | 2 | 22 |
| 69 | `175-176` | 2 | 22 |
| 70 | `177-178` | 2 | 24 |
| 71 | `179-180` | 2 | 21 |
| 72 | `181-183` | 3 | 24 |
| 73 | `184-185` | 2 | 19 |
| 74 | `186-187` | 2 | 19 |
| 75 | `188-188` | 1 | 17 |
| 76 | `189-190` | 2 | 21 |
| 77 | `191-192` | 2 | 17 |
| 78 | `193-196` | 4 | 26 |
| 79 | `197-198` | 2 | 14 |
| 80 | `199-201` | 3 | 24 |
| 81 | `202-203` | 2 | 23 |
| 82 | `204-205` | 2 | 21 |
| 83 | `206-206` | 1 | 17 |
| 84 | `207-208` | 2 | 23 |
| 85 | `209-212` | 4 | 25 |
| 86 | `213-214` | 2 | 24 |
| 87 | `215-217` | 3 | 25 |
| 88 | `218-219` | 2 | 14 |
| 89 | `220-221` | 2 | 23 |
| 90 | `222-223` | 2 | 21 |
| 91 | `224-225` | 2 | 22 |
| 92 | `226-228` | 3 | 26 |
| 93 | `229-235` | 7 | 25 |
| 94 | `236-238` | 3 | 26 |
| 95 | `239-241` | 3 | 18 |
| 96 | `242-245` | 3 | 19 |

The next compiler may consume one of these batches only after its Korean wording, control bytes, renderer family, and bounded runtime target are declared.

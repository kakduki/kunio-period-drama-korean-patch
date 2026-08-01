# Pre-Pointer Dialogue Overlap Audit

- Inventory rows: `250`.
- English dialogue owner runs: `722`.
- This audit classifies ownership only; it does not authorize a patch.

## Ownership Classes

| class | rows | meaning |
| --- | ---: | --- |
| `FULLY_CONTAINED` | 161 | The inventory byte range is inside one or more English dialogue runs. |
| `EDGE_OVERLAP` | 25 | The row crosses a dialogue-run boundary, often a control byte or separator. |
| `RUN_INSIDE_ROW` | 29 | The row is wider than the detected English run and needs boundary review. |
| `NO_OVERLAP` | 35 | No English dialogue run was found at this ROM range. |

## Readiness Breakdown

| readiness / class | rows |
| --- | ---: |
| `BLOCKED_CONTROL_SKELETON:EDGE_OVERLAP` | 5 |
| `BLOCKED_CONTROL_SKELETON:RUN_INSIDE_ROW` | 12 |
| `BLOCKED_MISSING_GLYPH:EDGE_OVERLAP` | 3 |
| `BLOCKED_MISSING_GLYPH:FULLY_CONTAINED` | 18 |
| `BLOCKED_MISSING_GLYPH:RUN_INSIDE_ROW` | 12 |
| `MAPPED_RUNTIME_UNKNOWN:FULLY_CONTAINED` | 10 |
| `UNMAPPED_GLOSSARY:EDGE_OVERLAP` | 17 |
| `UNMAPPED_GLOSSARY:FULLY_CONTAINED` | 133 |
| `UNMAPPED_GLOSSARY:NO_OVERLAP` | 35 |
| `UNMAPPED_GLOSSARY:RUN_INSIDE_ROW` | 5 |

## Bounded Patch Candidates

The current safe subset contains `10` rows: `EN-PRE-112`, `EN-PRE-118`, `EN-PRE-119`, `EN-PRE-125`, `EN-PRE-129`, `EN-PRE-130`, `EN-PRE-134`, `EN-PRE-135`, `EN-PRE-138`, `EN-PRE-185`.

Rows with `FULLY_CONTAINED` ownership but missing Korean glyphs or translations remain blocked. Rows with `EDGE_OVERLAP` or `RUN_INSIDE_ROW` must retain their control/separator skeleton. No broad patch is authorized by this report alone.

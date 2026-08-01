# Full Pointer Translation Audit

Status: **PASS**

- Rows: `248`; active: `244`; excluded: `4`.
- Structurally valid translations: `244` / `244`.
- Semantically reviewed rows: `244` / `244`.
- Translation statuses: `{'english_reference_reviewed': 244, 'excluded_non_dialogue': 4}`.
- Failures: `{}`.
- Warnings: `{'dynamic_control_context': 47}`.

The English patch is the semantic and control-structure reference. The
Current Korean rows compile cleanly and all active rows passed the
English-reference semantic review. Forty-seven dynamic control contexts
remain flagged for screen-specific review; runtime/layout PASS is not
whole-game visual approval.

The CSV companion contains every English line, Korean draft, actual
compiled display text, notes, and row-level findings for review.

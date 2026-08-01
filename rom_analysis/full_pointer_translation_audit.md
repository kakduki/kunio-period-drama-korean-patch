# Full Pointer Translation Audit

Status: **PASS**

- Rows: `248`; active: `244`; excluded: `4`.
- Structurally valid translations: `244` / `244`.
- Semantically reviewed rows: `244` / `244`.
- Translation statuses: `{'english_reference_reviewed': 244, 'excluded_non_dialogue': 4}`.
- Failures: `{}`.
- Warnings: `{'dynamic_control_context': 47}`.

The English patch is the semantic and control-structure reference. The
current Korean rows compile cleanly, but all active rows are still marked
as semantic drafts. Runtime and layout PASS results therefore do not yet
constitute translation approval.

The CSV companion contains every English line, Korean draft, actual
compiled display text, notes, and row-level findings for review.

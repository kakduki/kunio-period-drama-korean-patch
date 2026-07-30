# Full Pointer Translation Audit

Status: **STRUCTURAL_PASS_TRANSLATION_REVIEW_REQUIRED**

- Rows: `248`; active: `244`; excluded: `4`.
- Structurally valid translations: `244` / `244`.
- Semantically reviewed rows: `38` / `244`.
- Translation statuses: `{'english_reference_reviewed': 38, 'english_semantic_draft': 206, 'excluded_non_dialogue': 4}`.
- Failures: `{}`.
- Warnings: `{'context_confirmation_required': 203, 'dynamic_control_context': 27, 'semantic_draft_not_reviewed': 206}`.

The English patch is the semantic and control-structure reference. The
current Korean rows compile cleanly, but all active rows are still marked
as semantic drafts. Runtime and layout PASS results therefore do not yet
constitute translation approval.

The CSV companion contains every English line, Korean draft, actual
compiled display text, notes, and row-level findings for review.

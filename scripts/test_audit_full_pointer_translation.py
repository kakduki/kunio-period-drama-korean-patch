#!/usr/bin/env python3
"""Test the full-pointer translation audit."""

from __future__ import annotations

from audit_full_pointer_translation import (
    DEFAULT_DRAFT,
    DEFAULT_ENGLISH,
    build_audit,
    english_pointer_rows,
    load_tsv,
)


def main() -> int:
    payload = build_audit(
        load_tsv(DEFAULT_DRAFT),
        english_pointer_rows(load_tsv(DEFAULT_ENGLISH)),
    )
    coverage = payload["coverage"]
    assert payload["status"] == "STRUCTURAL_PASS_TRANSLATION_REVIEW_REQUIRED"
    assert payload["structural_status"] == "PASS"
    assert payload["translation_status"] == "REVIEW_REQUIRED"
    assert coverage["row_count"] == 248
    assert coverage["active_count"] == 244
    assert coverage["excluded_count"] == 4
    assert coverage["reviewed_count"] == 189
    assert coverage["failure_counts"] == {}
    assert coverage["warning_counts"]["semantic_draft_not_reviewed"] == 55
    assert coverage["warning_counts"]["dynamic_control_context"] == 36
    assert len(payload["rows"]) == 248
    print("Full pointer translation audit tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

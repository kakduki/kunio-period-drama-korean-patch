#!/usr/bin/env python3
"""Test the full Korean pointer-dialogue draft audit."""

from __future__ import annotations

import json

from analyze_pointer_dialogue_korean_draft import (
    DEFAULT_CHAR_MAP,
    DEFAULT_DRAFT,
    DEFAULT_ENGLISH,
    build_payload,
    english_pointer_rows,
    load_tsv,
    validate_draft,
)


def main() -> int:
    draft = validate_draft(load_tsv(DEFAULT_DRAFT))
    english = english_pointer_rows(load_tsv(DEFAULT_ENGLISH))
    char_map = set(json.loads(DEFAULT_CHAR_MAP.read_text(encoding="utf-8"))["sorted"])
    payload = build_payload(draft, english, char_map)
    assert payload["status"] == "FULL_DRAFT_CAPACITY_BLOCKED"
    assert payload["draft"]["row_count"] == 248
    assert payload["draft"]["active_row_count"] == 244
    assert payload["font_capacity"]["proven_source_code_count"] == 26
    assert payload["font_capacity"]["unique_non_space_symbols"] > 26
    assert payload["space_estimate"]["estimated_compiled_bytes"] < payload["space_estimate"]["available_bytes"]
    assert payload["recommended_batches"]
    print("Pointer dialogue Korean draft audit tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

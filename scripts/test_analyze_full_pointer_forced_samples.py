#!/usr/bin/env python3
"""Test committed full-pointer forced runtime samples."""

from __future__ import annotations

from analyze_full_pointer_forced_samples import DEFAULT_INPUT, build_report


def main() -> int:
    payload = build_report(DEFAULT_INPUT)
    assert payload["status"] == "PASS"
    assert payload["coverage"]["sample_count"] == 5
    assert payload["coverage"]["distinct_page_count"] == 5
    assert payload["coverage"]["page_indices"] == [11, 16, 32, 41, 42]
    assert all(sample["checks"]["mapper_r1_matches"] for sample in payload["samples"])
    assert all(sample["checks"]["source_reached_terminator"] for sample in payload["samples"])
    assert all(sample["checks"]["field_background_present"] for sample in payload["samples"])
    assert all(sample["image"]["field_unique_colors"] == 14 for sample in payload["samples"])
    print("Full pointer forced sample analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

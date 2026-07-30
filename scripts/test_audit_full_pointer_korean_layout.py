#!/usr/bin/env python3
"""Test the full pointer Korean layout audit."""

from __future__ import annotations

from audit_full_pointer_korean_layout import (
    HARD_CELL_LIMIT,
    build_audit,
    display_segment_lengths,
)
from build_full_pointer_korean_candidate import build_config
from build_ptr181_bank8_page_probe import resolve_base_rom


def main() -> int:
    assert display_segment_lengths(bytes.fromhex("81 82 00 83 CA 84 FF")) == [4, 1]
    config = build_config(resolve_base_rom(None).read_bytes())
    payload = build_audit(config)
    assert payload["status"] == "PASS"
    assert payload["coverage"]["active_records"] == 244
    assert payload["coverage"]["maximum_segment_cells"] == HARD_CELL_LIMIT
    assert payload["coverage"]["failure_count"] == 0
    assert payload["coverage"]["warning_count"] == 2

    risky = {
        "records": [
            {
                "record": bytes([0x81]) * (HARD_CELL_LIMIT + 1) + b"\xff",
                "excluded": False,
                "pointer_index": 7,
                "page_index": 0,
                "korean_text": "가",
            }
        ]
    }
    assert build_audit(risky)["status"] == "FAIL"
    print("Full pointer Korean layout audit tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

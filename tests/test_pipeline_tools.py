#!/usr/bin/env python3
"""Dependency-free unit tests for the reproducible analysis helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from _analysis_common import apply_ips, changed_spans, pointer_candidates  # noqa: E402


class PipelineToolTests(unittest.TestCase):
    def test_ips_payload_and_rle_records(self) -> None:
        base = bytes(range(16))
        patch = b"PATCH" + bytes.fromhex("0000020002 AABB") + bytes.fromhex("0000080000 0003 CC") + b"EOF"
        self.assertEqual(apply_ips(base, patch)[2:4], b"\xAA\xBB")
        self.assertEqual(apply_ips(base, patch)[8:11], b"\xCC\xCC\xCC")

    def test_changed_spans_include_growth(self) -> None:
        self.assertEqual(changed_spans(b"abc", b"abXyz"), [(2, 5)])

    def test_pointer_candidates_keep_cpu_context(self) -> None:
        data = bytes.fromhex("00 80 34 12 FF FF")
        rows = pointer_candidates(data, 0, len(data))
        self.assertEqual(rows[0]["cpu_address"], 0x8000)
        self.assertIn(0xFFFF, [row["cpu_address"] for row in rows])


if __name__ == "__main__":
    unittest.main()

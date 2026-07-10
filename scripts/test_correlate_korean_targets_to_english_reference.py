#!/usr/bin/env python3
"""Regression checks for Korean target correlation against English IPS runs."""
from __future__ import annotations

import unittest

from correlate_korean_targets_to_english_reference import correlate
from rom_utils import REPO_ROOT


class KoreanTargetCorrelationTests(unittest.TestCase):
    def test_all_v043_targets_are_classified_without_runtime_promotion(self) -> None:
        result = correlate(
            REPO_ROOT / "rom_analysis" / "v043_proof_status.json",
            REPO_ROOT / "analysis" / "english_reference_runs.json",
            REPO_ROOT / "rom" / "kunio.nes",
        )
        rows = result["rows"]
        self.assertEqual(len(rows), 7)
        self.assertEqual({row["classification"] for row in rows}, {"structurally_supported", "unrelated_to_english_reference"})
        self.assertEqual(sum(row["classification"] == "structurally_supported" for row in rows), 5)
        self.assertEqual(sum(row["classification"] == "unrelated_to_english_reference" for row in rows), 2)
        self.assertTrue(all(row["runtime_proof_required"] is True for row in rows))
        self.assertTrue(all(row["release_ready"] is False for row in rows))

    def test_offset_is_a_file_offset_and_original_bytes_are_verified(self) -> None:
        result = correlate(
            REPO_ROOT / "rom_analysis" / "v043_proof_status.json",
            REPO_ROOT / "analysis" / "english_reference_runs.json",
            REPO_ROOT / "rom" / "kunio.nes",
        )
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["offset_convention"]["header_bytes"], 16)
        self.assertEqual(result["offset_convention"]["intervals"], "start inclusive, end_exclusive")
        first = result["rows"][0]
        self.assertEqual(first["offset_convention"], "iNES file offset including 16-byte header")
        self.assertEqual(first["base_bytes_verified"], True)
        self.assertEqual(first["file_offset"], 0x440C)

    def test_supported_rows_have_traceable_run_ids(self) -> None:
        result = correlate(
            REPO_ROOT / "rom_analysis" / "v043_proof_status.json",
            REPO_ROOT / "analysis" / "english_reference_runs.json",
            REPO_ROOT / "rom" / "kunio.nes",
        )
        for row in result["rows"]:
            if row["classification"] == "structurally_supported":
                self.assertTrue(row["overlap_run_ids"])
                self.assertTrue(row["overlap_ranges"])
            else:
                self.assertEqual(row["overlap_run_ids"], [])


if __name__ == "__main__":
    unittest.main()

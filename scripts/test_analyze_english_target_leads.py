#!/usr/bin/env python3
"""Regression checks for static English-reference target leads."""
from __future__ import annotations

import unittest

from analyze_english_target_leads import analyze
from rom_utils import REPO_ROOT


class EnglishTargetLeadTests(unittest.TestCase):
    def test_emits_only_supported_targets_as_static_leads(self) -> None:
        result = analyze(
            REPO_ROOT / "analysis" / "korean_target_english_reference_correlation.json",
            REPO_ROOT / "analysis" / "english_reference_runs.json",
            REPO_ROOT / "rom" / "kunio.nes",
            REPO_ROOT / "reference" / "technos-samurai-v1" / "TSe-v10.ips",
        )
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["lead_count"], 5)
        self.assertEqual([lead["task"] for lead in result["leads"]], [3, 4, 5, 6, 7])
        self.assertTrue(all(lead["classification"] == "static_only" for lead in result["leads"]))
        self.assertTrue(all(lead["runtime_proof_required"] is True for lead in result["leads"]))
        self.assertTrue(all(lead["release_ready"] is False for lead in result["leads"]))

    def test_leads_preserve_exact_reference_bytes_and_overlap(self) -> None:
        result = analyze(
            REPO_ROOT / "analysis" / "korean_target_english_reference_correlation.json",
            REPO_ROOT / "analysis" / "english_reference_runs.json",
            REPO_ROOT / "rom" / "kunio.nes",
            REPO_ROOT / "reference" / "technos-samurai-v1" / "TSe-v10.ips",
        )
        first = result["leads"][0]
        self.assertEqual(first["file_offset"], 0x052A5)
        self.assertEqual(first["base_bytes"], "82 84 7E")
        self.assertEqual(len(bytes.fromhex(first["english_bytes"])), 3)
        self.assertEqual(first["overlap_ranges"][0]["overlap_bytes"], 2)
        self.assertTrue(first["english_target_bytes_differ"])

    def test_pointer_hits_are_explicitly_mapper_unknown_candidates(self) -> None:
        result = analyze(
            REPO_ROOT / "analysis" / "korean_target_english_reference_correlation.json",
            REPO_ROOT / "analysis" / "english_reference_runs.json",
            REPO_ROOT / "rom" / "kunio.nes",
            REPO_ROOT / "reference" / "technos-samurai-v1" / "TSe-v10.ips",
        )
        for lead in result["leads"]:
            self.assertEqual(lead["pointer_scan"]["status"], "mapper_unknown_static_candidates")
            self.assertEqual(lead["pointer_scan"]["cpu_address_candidates"], 4)
            self.assertIn("opcode_absolute_operand_hits", lead["pointer_scan"])
            self.assertNotIn("runtime_proof", lead["pointer_scan"])


if __name__ == "__main__":
    unittest.main()

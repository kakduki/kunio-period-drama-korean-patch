#!/usr/bin/env python3
"""Regression checks for the static English IPS run map."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from analyze_english_reference_runs import analyze, parse_ips
from rom_utils import REPO_ROOT


BASE = REPO_ROOT / "rom" / "kunio.nes"
IPS = REPO_ROOT / "reference" / "technos-samurai-v1" / "TSe-v10.ips"


class EnglishReferenceRunMapTests(unittest.TestCase):
    def test_verified_reference_has_complete_record_and_region_map(self) -> None:
        result = analyze(BASE, IPS)
        self.assertEqual(result["base"]["md5"], "0d406a85285b4de8468f0dab6aad5fe5")
        self.assertEqual(
            result["ips"]["sha256"],
            "cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad",
        )
        self.assertEqual(result["ips"]["records"], 99)
        self.assertEqual(len(result["records"]), 99)
        self.assertEqual(result["changed_bytes_by_region"], {"header": 1, "prg": 10295, "chr": 2286})
        self.assertTrue(all(run["end_exclusive"] > run["start"] for run in result["runs"]))
        self.assertTrue(all("physical_bank" in run for run in result["runs"]))
        self.assertEqual(result["records"][0]["region"], "header")

    def test_runs_never_join_an_actual_gap(self) -> None:
        result = analyze(BASE, IPS)
        for previous, current in zip(result["runs"], result["runs"][1:]):
            self.assertGreater(current["start"], previous["end_exclusive"])

    def test_rejects_base_digest_mismatch(self) -> None:
        broken = bytearray(BASE.read_bytes())
        broken[16] ^= 0x01
        with tempfile.TemporaryDirectory() as temp_dir:
            wrong_base = Path(temp_dir) / "wrong.nes"
            wrong_base.write_bytes(broken)
            with self.assertRaisesRegex(ValueError, "base ROM MD5"):
                analyze(wrong_base, IPS)

    def test_parser_exposes_all_ips_records(self) -> None:
        self.assertEqual(len(parse_ips(IPS.read_bytes())), 99)
        self.assertEqual(hashlib.sha256(IPS.read_bytes()).hexdigest()[:8], "cb6ea2fd")


if __name__ == "__main__":
    unittest.main()

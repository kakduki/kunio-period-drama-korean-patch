#!/usr/bin/env python3
"""Focused tests for the bounded candidate-pipeline artifact generator."""

from __future__ import annotations

from generate_readability_proof_artifacts import OUTPUT_FILES, render_artifacts


def main() -> int:
    artifacts = render_artifacts()
    assert tuple(artifacts) == OUTPUT_FILES
    assert "opening_ptr_182_16x16_readability_proof" in artifacts["build_matrix.md"]
    assert "PASS_FOR_OPENING_PROOF_ONLY" in artifacts["string_candidates.csv"]
    assert "Raw 0xBB inside dialogue records" in artifacts["false_positive_list.csv"]
    assert "PROOF_CANDIDATE_VISUALLY_VERIFIED" in artifacts["patched_rom_report.md"]
    assert "matched_read_hits=38" in artifacts["smoke_test_log.txt"]
    assert "NOT_READY_FOR_RELEASE" in artifacts["release_gate_checklist.md"]
    print("Readability proof pipeline artifact tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

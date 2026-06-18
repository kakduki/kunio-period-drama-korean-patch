#!/usr/bin/env python3
"""Tests for state cheat probe candidate reporting."""

from __future__ import annotations

from generate_state_cheat_probe_candidates import OUT_MD, make_payload, write_markdown


def test_state_cheat_probe_candidates_have_sources() -> None:
    payload = make_payload()

    assert payload["summary"]["snapshots"] >= 2
    assert payload["summary"]["candidate_addresses"] > 0
    assert payload["top_candidates"]


def test_state_cheat_probe_markdown_names_next_probe() -> None:
    payload = make_payload()
    write_markdown(payload)
    text = OUT_MD.read_text(encoding="utf-8")

    assert "# State Cheat Probe Candidates" in text
    assert "Avoid broad writes" in text
    assert "Top RAM Candidates" in text


if __name__ == "__main__":
    test_state_cheat_probe_candidates_have_sources()
    test_state_cheat_probe_markdown_names_next_probe()

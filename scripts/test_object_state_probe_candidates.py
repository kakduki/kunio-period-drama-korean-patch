#!/usr/bin/env python3
"""Tests for object/enemy-state probe candidate reporting."""

from __future__ import annotations

from generate_object_state_probe_candidates import OUT_MD, make_payload, write_markdown


def test_object_state_probe_candidates_are_object_range() -> None:
    payload = make_payload()

    assert payload["summary"]["candidate_addresses"] > 0
    for row in payload["top_candidates"]:
        address = int(str(row["address"]), 16)
        assert 0x0300 <= address <= 0x04FF
        assert "slot_hint" in row


def test_object_state_probe_markdown_names_next_probe() -> None:
    payload = make_payload()
    write_markdown(payload)
    text = OUT_MD.read_text(encoding="utf-8")

    assert "# Object State Probe Candidates" in text
    assert "one address and one value at a time" in text
    assert "Top Object/Enemy Candidates" in text


if __name__ == "__main__":
    test_object_state_probe_candidates_are_object_range()
    test_object_state_probe_markdown_names_next_probe()

#!/usr/bin/env python3
"""Tests for object-state paired probe planning."""

from __future__ import annotations

from generate_object_state_pair_plan import OUT_MD, make_payload, write_markdown


def test_object_state_pair_plan_has_blocks() -> None:
    payload = make_payload()

    assert payload["summary"]["candidate_blocks"] > 0
    assert payload["top_blocks"]
    assert payload["top_blocks"][0]["recommended_probe"]


def test_object_state_pair_plan_markdown() -> None:
    payload = make_payload()
    write_markdown(payload)
    text = OUT_MD.read_text(encoding="utf-8")

    assert "# Object State Pair Plan" in text
    assert "Recommended paired probe" in text
    assert "Next Probe" in text


if __name__ == "__main__":
    test_object_state_pair_plan_has_blocks()
    test_object_state_pair_plan_markdown()

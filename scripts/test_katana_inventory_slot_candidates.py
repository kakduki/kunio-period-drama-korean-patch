#!/usr/bin/env python3
"""Tests for Katana inventory slot candidate ranking."""

from __future__ import annotations

from generate_katana_inventory_slot_candidates import OUT_MD, make_payload, write_markdown


def test_candidate_report_excludes_menu_state() -> None:
    payload = make_payload()
    rows = {row["address"]: row for row in payload["rows"]}

    assert rows["0x7700"]["classification"] == "exclude_menu_state"
    assert rows["0x0502"]["classification"] == "candidate_small_probe"
    assert payload["summary"]["classification_counts"]["candidate_small_probe"] == 5
    assert payload["summary"]["completed_single_slot_probes"] == ["0x0502", "0x0503"]


def test_candidate_markdown_names_next_probe() -> None:
    payload = make_payload()
    write_markdown(payload)
    text = OUT_MD.read_text(encoding="utf-8")

    assert "# Katana Inventory Slot Candidates" in text
    assert "continue with 0x0506" in text
    assert "`exclude_menu_state`" in text


if __name__ == "__main__":
    test_candidate_report_excludes_menu_state()
    test_candidate_markdown_names_next_probe()

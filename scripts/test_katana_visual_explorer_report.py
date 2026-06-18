#!/usr/bin/env python3
"""Tests for the Katana visual explorer report."""

from __future__ import annotations

from generate_katana_visual_explorer_report import OUT_MD, make_payload, write_markdown


def test_katana_report_records_item_list_but_no_visual_approval() -> None:
    payload = make_payload()
    summary = payload["summary"]

    assert summary["item_list_frame"] == "2385"
    assert summary["katana_active_match_on_item_list"] == "false"
    assert "Do not mark Katana visually confirmed" in summary["decision"]


def test_katana_report_links_key_review_frames() -> None:
    payload = make_payload()
    write_markdown(payload)
    text = OUT_MD.read_text(encoding="utf-8")

    assert "manual_frame_001906_screen.png" in text
    assert "manual_frame_002385_screen.png" in text
    assert "item-list context" in text


if __name__ == "__main__":
    test_katana_report_records_item_list_but_no_visual_approval()
    test_katana_report_links_key_review_frames()

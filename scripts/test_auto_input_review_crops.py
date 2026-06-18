#!/usr/bin/env python3
"""Tests for auto-input review crop generation."""

from __future__ import annotations

import json

from generate_auto_input_review_crops import OUT_JSON, OUT_MD, make_crops, write_report


def test_review_crops_are_generated_for_all_checked_in_screens() -> None:
    payload = make_crops()

    assert payload["crop_count"] == 8
    paths = {row["path"] for row in payload["crops"]}
    assert "rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen_dialogue_box.png" in paths
    assert "rom_analysis/fceux_input_explorer_v042/manual_frame_000883_screen_top_overlay.png" in paths


def test_review_crop_report_mentions_dialogue_box() -> None:
    payload = make_crops()
    write_report(payload)
    text = OUT_MD.read_text(encoding="utf-8")

    assert "# Auto-Input Review Crops" in text
    assert "`dialogue_box`" in text
    assert "manual_frame_000883_screen_dialogue_box.png" in text
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["crop_count"] == 8


if __name__ == "__main__":
    test_review_crops_are_generated_for_all_checked_in_screens()
    test_review_crop_report_mentions_dialogue_box()

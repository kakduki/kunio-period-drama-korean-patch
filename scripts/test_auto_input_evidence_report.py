#!/usr/bin/env python3
"""Tests for the auto-input evidence report."""

from __future__ import annotations

import json

from generate_auto_input_evidence_report import OUT_JSON, OUT_MD, make_payload, write_markdown


def test_payload_summarizes_auto_input_matches() -> None:
    payload = make_payload()
    summary = payload["summary"]

    assert int(summary["matched_primary_rows"]) == 10
    assert str(summary["latest_png_review_image"]).endswith("manual_frame_000883_screen.png")
    assert "visually correct" in str(summary["current_limit"])


def test_markdown_mentions_limit_and_matched_rows() -> None:
    payload = make_payload()
    write_markdown(payload)
    text = OUT_MD.read_text(encoding="utf-8")

    assert "# Auto-Input Evidence Report" in text
    assert "0x07227" in text
    assert "does not by itself prove" in text


if __name__ == "__main__":
    test_payload_summarizes_auto_input_matches()
    test_markdown_mentions_limit_and_matched_rows()
    data = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else make_payload()
    assert data["summary"]["matched_primary_rows"] == 10

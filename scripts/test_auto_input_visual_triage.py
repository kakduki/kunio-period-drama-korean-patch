#!/usr/bin/env python3
"""Tests for auto-input visual triage."""

from __future__ import annotations

import json

from generate_auto_input_visual_triage import OUT_JSON, OUT_MD, make_payload, write_markdown


def test_visual_triage_does_not_overapprove_byte_matches() -> None:
    payload = make_payload()
    summary = payload["summary"]

    assert int(summary["byte_matched_primary_rows"]) == 10
    assert int(summary["visual_approval_rows"]) == 0
    assert summary["next_visual_target"] == "0x07227"
    assert str(summary["latest_dialogue_crop"]).endswith("manual_frame_000883_screen_dialogue_box.png")


def test_visual_triage_report_states_next_context() -> None:
    payload = make_payload()
    write_markdown(payload)
    text = OUT_MD.read_text(encoding="utf-8")
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))

    assert "# Auto-Input Visual Triage" in text
    assert "Do not mark any primary row visually confirmed" in text
    assert "`0x07227` / Katana" in text
    assert data["summary"]["visual_approval_rows"] == 0


if __name__ == "__main__":
    test_visual_triage_does_not_overapprove_byte_matches()
    test_visual_triage_report_states_next_context()

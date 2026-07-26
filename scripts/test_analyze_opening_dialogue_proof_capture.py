#!/usr/bin/env python3
"""Focused tests for opening-dialogue proof-capture classification."""

from __future__ import annotations

import tempfile
from pathlib import Path

from analyze_opening_dialogue_proof_capture import analyze_capture


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp)
        (root / "summary.tsv").write_text(
            "frame\treason\tregistered\thits\tdetail\n883\tcapture\t37\t4\tok\n883\tlua_done\t37\t4\tcaptured=true\n",
            encoding="utf-8",
        )
        (root / "opening_target_reads.tsv").write_text(
            "frame\tlabel\tcpu_addr\tvalue\tactive_expected_match\trecord_snapshot\n880\ttarget\t$B1A6\t81\ttrue\t81 82\n",
            encoding="utf-8",
        )
        (root / "opening_target_record.tsv").write_text(
            "frame\tlabel\tcpu_range\texpected_bytes\tactive_expected_match\trecord_snapshot\n883\ttarget\t$B1A6-$B1CA\t81 82\ttrue\t81 82\n",
            encoding="utf-8",
        )
        (root / "opening_dialogue_frame_000883_screen.gd").write_bytes(b"gd")
        (root / "opening_dialogue_frame_000883_nametable_2000_23bf.bin").write_bytes(b"nt")
        payload = analyze_capture(root)
        assert payload["overall_smoke"] == "PASS"
        assert payload["checks"]["target_record_runtime_read"] == "PASS"
        assert payload["checks"]["visual_korean_glyph_review"] == "UNKNOWN"
        visual_payload = analyze_capture(
            root,
            visual_verdict="PASS",
            visual_note="Korean glyphs reviewed in the captured scene.",
        )
        assert visual_payload["overall_proof"] == "PASS"
        assert visual_payload["status"] == "PROOF_CANDIDATE_VISUALLY_VERIFIED"
    print("Opening dialogue proof capture analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Test forced boss-dialogue capture classification."""

from __future__ import annotations

import tempfile
from pathlib import Path

from summarize_boss_forced_render import build_report


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        targets = root / "targets.csv"
        write(targets, "pointer_index\n001\n002\n")
        good = root / "ptr001"
        write(good / "forced_pointer.tsv", "frame\tpointer_index\n1\t1\n")
        write(good / "source_reads.tsv", "frame\taddress\tsource_byte\n1\tA000\t94\n2\tA001\t91\n")
        write(good / "parser_exec.tsv", "frame\tlabel\n1\temit_dispatch\n")
        write(good / "ppu_writes.tsv", "frame\n1\n")
        write(good / "summary.tsv", "frame\treason\ttarget_seen\n392\tcapture\ttrue\n")
        (good / "frame_000392_screen.gd").write_bytes(b"screen")
        unknown = root / "ptr002"
        write(unknown / "source_reads.tsv", "frame\taddress\tsource_byte\n1\tA100\tF0\n")
        write(unknown / "ppu_writes.tsv", "frame\n1\n")
        write(unknown / "summary.tsv", "frame\treason\ttarget_seen\n392\tcapture\ttrue\n")
        (unknown / "frame_000392_screen.gd").write_bytes(b"screen")
        report = build_report(targets, root)
        assert report["forced_render_pass_count"] == 1
        assert report["rows"][0]["forced_render_status"] == "PASS_FORCED_BOSS_DIALOGUE_RENDER"
        assert report["rows"][1]["forced_render_status"] == "UNKNOWN_FORCED_POINTER_ONLY"
        assert all(row["natural_route_status"] == "UNKNOWN" for row in report["rows"])
    print("OK: forced boss renderer captures are classified without promoting natural-route proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

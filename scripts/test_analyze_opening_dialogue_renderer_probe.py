#!/usr/bin/env python3
"""Focused tests for opening-dialogue renderer trace classification."""

from __future__ import annotations

import tempfile
from pathlib import Path

from analyze_opening_dialogue_renderer_probe import classify


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write(root / "summary.tsv", "frame\treason\n0\tlua_start\n883\tlua_done\n")
        write(
            root / "parser_exec.tsv",
            "frame\tlabel\tpc\tsource_byte\n650\tparser\t8246\t81\n650\temit_prep\t8432\t81\n650\temit_dispatch\t843E\t81\n",
        )
        write(root / "source_reads.tsv", "frame\taddress\tpc\n650\tB1A6\t9ABC\n")
        write(root / "buffer_writes.tsv", "frame\taddress\n650\t7000\n")
        write(root / "queue_writes.tsv", "frame\taddress\n650\t711D\n")
        write(
            root / "emitted_tiles.tsv",
            "frame\trole\taddress\tvalue\tpc\ty\tsource_byte\tmapper_control\tmapper_select\tppu_control\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\n"
            "650\ttop\t7139\t81\t95AE\t00\t81\t07\t1\t8C\t3C\t3E\t30\t31\t32\t33\t02\t03\n",
        )
        write(root / "dma.tsv", "frame\tpage\n650\t02\n")
        write(root / "oam_writes.tsv", "frame\taddress\n650\t0201\n")
        write(root / "ppu_writes.tsv", "frame\ttype\n650\tdata\n")
        write(root / "ppu_rows.tsv", "row\tvalues\n" + "\n".join(f"{row}\t00" for row in range(30)) + "\n")
        (root / "renderer_probe_frame_000883_screen.gd").write_bytes(b"gd")
        payload = classify(root)
    assert payload["status"] == "ROUTINE_TRACE_CAPTURED"
    assert payload["checks"]["target_parser_execution"] == "PASS"
    assert payload["checks"]["target_source_reads"] == "PASS"
    assert payload["checks"]["renderer_buffer_writes"] == "PASS"
    assert payload["checks"]["renderer_queue_writes"] == "PASS"
    assert payload["checks"]["target_emitted_tile_rows"] == "PASS"
    assert payload["checks"]["dialogue_nametable_writes"] == "PASS"
    assert payload["checks"]["ppu_rows_captured"] == "PASS"
    print("Opening dialogue renderer probe analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
